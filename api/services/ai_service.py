"""
AI Service - Gemini-powered media analysis, tagging, and semantic search.
Uses ChromaDB for local vector storage and Google Gemini for vision + embeddings.
"""
import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.job_manager import job_manager

logger = logging.getLogger("AIService")

# Lazy-loaded globals
_genai = None
_model = None
_chroma_client = None
_collection = None

IMAGE_EXTENSIONS = {'.heic', '.jpg', '.jpeg', '.png', '.webp', '.gif', '.dng', '.arw', '.cr2', '.nef'}
THUMBNAIL_MAX_SIZE = (512, 512)
CHROMA_DB_PATH = str(Path(__file__).parent.parent / ".chromadb")


def _get_genai():
    """Lazy-initialize the Gemini SDK."""
    global _genai, _model
    if _genai is None:
        import google.generativeai as genai

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Get one at https://aistudio.google.com/apikey"
            )
        genai.configure(api_key=api_key)
        _genai = genai
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _genai, _model


def _get_collection():
    """Lazy-initialize ChromaDB collection."""
    global _chroma_client, _collection
    if _collection is None:
        import chromadb

        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _collection = _chroma_client.get_or_create_collection(
            name="media_index",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def _generate_thumbnail(file_path: Path) -> Optional[bytes]:
    """Generate an in-memory JPEG thumbnail for API upload."""
    from PIL import Image
    import io

    try:
        img = Image.open(file_path)
        img.thumbnail(THUMBNAIL_MAX_SIZE)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return buffer.getvalue()
    except Exception as e:
        logger.warning(f"Could not generate thumbnail for {file_path.name}: {e}")
        return None


def _file_cache_id(file_path: Path) -> str:
    """Generate a stable cache ID from path + modification time."""
    mtime = file_path.stat().st_mtime
    raw = f"{str(file_path)}:{mtime}"
    return hashlib.md5(raw.encode()).hexdigest()


def analyze_image(file_path: str) -> Dict[str, Any]:
    """
    Analyze a single image using Gemini Vision.
    Returns structured tags: scene, objects, quality, etc.
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": "File not found"}

    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        return {"error": f"Unsupported file type: {path.suffix}"}

    thumb_bytes = _generate_thumbnail(path)
    if thumb_bytes is None:
        return {"error": "Could not read image"}

    genai, model = _get_genai()

    prompt = """Analyze this image and return a JSON object with these fields:
{
  "description": "one-sentence description of the image",
  "scene": "indoor/outdoor/closeup/aerial/screenshot/document",
  "objects": ["list", "of", "main", "objects"],
  "tags": ["semantic", "tags", "for", "search"],
  "people_count": 0,
  "quality_score": 8,
  "is_screenshot": false,
  "is_blurry": false,
  "dominant_colors": ["#hex1", "#hex2"],
  "suggested_folder": "a suggested folder name like 'Vacation', 'Food', 'Documents'"
}
Return ONLY the JSON, no markdown fences."""

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": thumb_bytes}
        ])

        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        result = json.loads(text)
        result["file"] = path.name
        result["path"] = str(path)
        result["analyzed_at"] = datetime.now().isoformat()
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response for {path.name}: {e}")
        return {"error": "Invalid AI response", "file": path.name, "raw": text[:200]}
    except Exception as e:
        logger.error(f"Gemini API error for {path.name}: {e}")
        return {"error": str(e), "file": path.name}


def index_media_library(
    source_dir: str,
    job_id: Optional[str] = None,
    force_reindex: bool = False
) -> Dict[str, Any]:
    """
    Walk a directory, analyze each image with Gemini, store in ChromaDB.
    Follows the same JobManager pattern as media_service.
    """
    source = Path(source_dir)
    if not source.exists():
        if job_id:
            job_manager.fail_job(job_id, "Source directory not found")
        return {"error": "Source directory not found"}

    collection = _get_collection()

    # Collect image files
    all_files = [
        p for p in source.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    total = len(all_files)

    if job_id:
        job_manager.start_job(job_id, total)

    results = {"indexed": 0, "skipped": 0, "errors": 0, "total": total, "details": []}

    for i, file_path in enumerate(all_files):
        # Check for abort
        if job_id and job_manager.is_aborted(job_id):
            results["aborted"] = True
            results["message"] = f"Aborted after processing {i} of {total} files"
            job_manager.mark_aborted(job_id, results)
            return results

        cache_id = _file_cache_id(file_path)

        # Skip if already indexed (unless force)
        if not force_reindex:
            existing = collection.get(ids=[cache_id])
            if existing and existing["ids"]:
                results["skipped"] += 1
                if job_id:
                    job_manager.update_progress(
                        job_id, i + 1, total,
                        message=f"Skipped (cached): {file_path.name}",
                        current_file=file_path.name
                    )
                continue

        # Analyze
        if job_id:
            job_manager.update_progress(
                job_id, i + 1, total,
                message=f"Analyzing: {file_path.name}",
                current_file=file_path.name
            )

        analysis = analyze_image(str(file_path))

        if "error" in analysis:
            results["errors"] += 1
            results["details"].append({"file": file_path.name, "error": analysis["error"]})
            continue

        # Build searchable text
        search_text = " ".join([
            analysis.get("description", ""),
            analysis.get("scene", ""),
            " ".join(analysis.get("objects", [])),
            " ".join(analysis.get("tags", [])),
            analysis.get("suggested_folder", "")
        ])

        # Store in ChromaDB
        try:
            collection.upsert(
                ids=[cache_id],
                documents=[search_text],
                metadatas=[{
                    "path": str(file_path),
                    "name": file_path.name,
                    "description": analysis.get("description", ""),
                    "scene": analysis.get("scene", ""),
                    "tags": json.dumps(analysis.get("tags", [])),
                    "quality_score": analysis.get("quality_score", 0),
                    "is_screenshot": str(analysis.get("is_screenshot", False)),
                    "is_blurry": str(analysis.get("is_blurry", False)),
                    "suggested_folder": analysis.get("suggested_folder", ""),
                    "analyzed_at": analysis.get("analyzed_at", "")
                }]
            )
            results["indexed"] += 1
            results["details"].append({"file": file_path.name, "status": "indexed"})
        except Exception as e:
            logger.error(f"ChromaDB error for {file_path.name}: {e}")
            results["errors"] += 1

    if job_id:
        job_manager.complete_job(job_id, results)

    return results


def search_media(query: str, top_k: int = 10, source_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Semantic search across indexed media using ChromaDB.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return {"results": [], "message": "No indexed media. Run /ai/index first."}

    try:
        search_results = collection.query(
            query_texts=[query],
            n_results=min(top_k, collection.count())
        )

        results = []
        if search_results and search_results["ids"]:
            for idx, doc_id in enumerate(search_results["ids"][0]):
                meta = search_results["metadatas"][0][idx] if search_results["metadatas"] else {}
                distance = search_results["distances"][0][idx] if search_results["distances"] else 0

                # Filter by source_dir if specified
                if source_dir and not meta.get("path", "").startswith(source_dir):
                    continue

                results.append({
                    "file": meta.get("name", ""),
                    "path": meta.get("path", ""),
                    "description": meta.get("description", ""),
                    "scene": meta.get("scene", ""),
                    "tags": json.loads(meta.get("tags", "[]")),
                    "quality_score": meta.get("quality_score", 0),
                    "suggested_folder": meta.get("suggested_folder", ""),
                    "relevance_score": round(1 - distance, 3) if distance else 0
                })

        return {"query": query, "results": results, "total": len(results)}

    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "results": []}


def get_smart_suggestions(source_dir: str) -> Dict[str, Any]:
    """
    Analyze a sample of files and return AI-generated organization suggestions.
    """
    source = Path(source_dir)
    if not source.exists():
        return {"error": "Source directory not found"}

    all_images = [
        p for p in source.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    # Sample up to 20 images for suggestions
    import random
    sample = random.sample(all_images, min(20, len(all_images))) if all_images else []

    if not sample:
        return {"error": "No images found in directory"}

    analyses = []
    for img in sample:
        result = analyze_image(str(img))
        if "error" not in result:
            analyses.append(result)

    if not analyses:
        return {"error": "Could not analyze any images"}

    # Ask Gemini for organization suggestions
    _, model = _get_genai()

    summary = json.dumps([
        {
            "file": a["file"],
            "description": a.get("description", ""),
            "scene": a.get("scene", ""),
            "tags": a.get("tags", []),
            "suggested_folder": a.get("suggested_folder", "")
        }
        for a in analyses
    ], indent=2)

    prompt = f"""Based on these analyzed images from a user's media library, suggest an optimal folder structure.

Image analyses:
{summary}

Return a JSON object with:
{{
  "suggested_structure": {{
    "FolderName": ["file1.jpg", "file2.jpg"]
  }},
  "rationale": "Brief explanation of the organization logic",
  "total_files_analyzed": {len(analyses)}
}}
Return ONLY the JSON, no markdown fences."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return {"error": str(e)}
