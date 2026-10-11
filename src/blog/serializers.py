def serialize_post(post) -> dict:
    return {
        "id": post.id,
        "slug": post.slug,
        "title": post.title,
        "summary": post.summary,
        "content": post.content,
        "category": post.category.slug if post.category else None,
        "status": post.status,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }
