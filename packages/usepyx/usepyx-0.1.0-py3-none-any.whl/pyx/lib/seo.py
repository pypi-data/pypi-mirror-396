from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union, Any, Callable
from functools import wraps
import json

@dataclass
class OpenGraph:
    """Type-safe Open Graph Metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    site_name: Optional[str] = None
    images: List[str] = field(default_factory=list)
    locale: str = "en_US"
    type: str = "website"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class TwitterCard:
    """Type-safe Twitter Card Metadata"""
    card: str = "summary_large_image"
    title: Optional[str] = None
    description: Optional[str] = None
    site: Optional[str] = None
    creator: Optional[str] = None
    images: List[str] = field(default_factory=list)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class Metadata:
    """
    Enterprise-Grade Metadata Container.
    Validates and structures SEO data for PyX pages.
    """
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    canonical: Optional[str] = None
    open_graph: Optional[Union[OpenGraph, Dict[str, Any]]] = None
    twitter: Optional[Union[TwitterCard, Dict[str, Any]]] = None
    json_ld: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

    def __post_init__(self):
        # Auto-convert dicts to Dataclasses if needed
        if isinstance(self.open_graph, dict):
            self.open_graph = OpenGraph(**self.open_graph)
        if isinstance(self.twitter, dict):
            self.twitter = TwitterCard(**self.twitter)


class Head:
    """
    Head component to render meta tags.
    
    Usage:
        Head(
            Metadata(
                title="My Page",
                description="Page description",
                open_graph=OpenGraph(title="My Page", images=["/og.jpg"])
            )
        )
        
        # Or inline:
        Head(title="My Page", description="...")
    """
    
    def __init__(
        self,
        metadata: Metadata = None,
        title: str = None,
        description: str = None,
        keywords: List[str] = None,
        canonical: str = None,
        og_title: str = None,
        og_image: str = None,
        og_description: str = None,
        twitter_card: str = "summary_large_image",
        json_ld: Dict = None,
        **extra_meta
    ):
        if metadata:
            self.metadata = metadata
        else:
            og = None
            if og_title or og_image or og_description:
                og = OpenGraph(
                    title=og_title or title,
                    description=og_description or description,
                    images=[og_image] if og_image else []
                )
            
            twitter = TwitterCard(
                card=twitter_card,
                title=og_title or title,
                description=og_description or description,
                images=[og_image] if og_image else []
            )
            
            self.metadata = Metadata(
                title=title or "PyX App",
                description=description,
                keywords=keywords,
                canonical=canonical,
                open_graph=og,
                twitter=twitter,
                json_ld=json_ld
            )
        
        self.extra_meta = extra_meta
    
    def render(self) -> str:
        """Render to HTML head tags"""
        m = self.metadata
        tags = []
        
        # Basic meta
        tags.append(f'<title>{m.title}</title>')
        if m.description:
            tags.append(f'<meta name="description" content="{m.description}">')
        if m.keywords:
            tags.append(f'<meta name="keywords" content="{", ".join(m.keywords)}">')
        if m.authors:
            tags.append(f'<meta name="author" content="{", ".join(m.authors)}">')
        if m.canonical:
            tags.append(f'<link rel="canonical" href="{m.canonical}">')
        
        # Open Graph
        if m.open_graph:
            og = m.open_graph
            if og.title:
                tags.append(f'<meta property="og:title" content="{og.title}">')
            if og.description:
                tags.append(f'<meta property="og:description" content="{og.description}">')
            if og.url:
                tags.append(f'<meta property="og:url" content="{og.url}">')
            if og.site_name:
                tags.append(f'<meta property="og:site_name" content="{og.site_name}">')
            if og.type:
                tags.append(f'<meta property="og:type" content="{og.type}">')
            if og.locale:
                tags.append(f'<meta property="og:locale" content="{og.locale}">')
            for img in og.images:
                tags.append(f'<meta property="og:image" content="{img}">')
        
        # Twitter Card
        if m.twitter:
            tw = m.twitter
            tags.append(f'<meta name="twitter:card" content="{tw.card}">')
            if tw.title:
                tags.append(f'<meta name="twitter:title" content="{tw.title}">')
            if tw.description:
                tags.append(f'<meta name="twitter:description" content="{tw.description}">')
            if tw.site:
                tags.append(f'<meta name="twitter:site" content="{tw.site}">')
            if tw.creator:
                tags.append(f'<meta name="twitter:creator" content="{tw.creator}">')
            for img in tw.images:
                tags.append(f'<meta name="twitter:image" content="{img}">')
        
        # JSON-LD
        if m.json_ld:
            ld = m.json_ld if isinstance(m.json_ld, list) else [m.json_ld]
            for item in ld:
                tags.append(f'<script type="application/ld+json">{json.dumps(item)}</script>')
        
        # Extra meta
        for key, value in self.extra_meta.items():
            tags.append(f'<meta name="{key}" content="{value}">')
        
        return '\n'.join(tags)
    
    def __str__(self):
        return self.render()


def seo(
    title: str = None,
    description: str = None,
    og_image: str = None,
    keywords: List[str] = None,
    canonical: str = None,
    json_ld: Dict = None,
    **extra
):
    """
    Decorator to add SEO metadata to a page.
    
    Usage:
        @seo(
            title="My Blog Post",
            description="A great blog post",
            og_image="/images/post.jpg"
        )
        def blog_post(slug):
            return ui.div(...)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the page content
            content = func(*args, **kwargs)
            
            # Create head
            head = Head(
                title=title,
                description=description,
                og_image=og_image,
                keywords=keywords,
                canonical=canonical,
                json_ld=json_ld,
                **extra
            )
            
            # Attach metadata to content (for server to extract)
            if hasattr(content, '_seo'):
                content._seo = head
            else:
                # Wrap in a container
                content = type('SeowrappedContent', (), {
                    'content': content,
                    '_seo': head,
                    'render': lambda self: (
                        f"<!-- SEO -->\n{self._seo.render()}\n<!-- /SEO -->\n"
                        + (self.content.render() if hasattr(self.content, 'render') else str(self.content))
                    ),
                    '__str__': lambda self: self.render()
                })()
            
            return content
        return wrapper
    return decorator


class JSONLD:
    """
    Helper to generate Google-compliant JSON-LD Structured Data.
    Focuses on Rich Results: Product, Article, Breadcrumb, etc.
    """
    
    @staticmethod
    def article(headline: str, image: List[str], author_name: str, date_published: str, date_modified: str = None) -> Dict[str, Any]:
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": headline,
            "image": image,
            "author": {"@type": "Person", "name": author_name},
            "datePublished": date_published,
            "dateModified": date_modified or date_published
        }

    @staticmethod
    def product(name: str, image: List[str], description: str, sku: str, price: str, currency: str = "IDR", availability: str = "InStock") -> Dict[str, Any]:
        return {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "image": image,
            "description": description,
            "sku": sku,
            "offers": {
                "@type": "Offer",
                "url": "",
                "priceCurrency": currency,
                "price": price,
                "availability": f"https://schema.org/{availability}"
            }
        }
    
    @staticmethod
    def breadcrumb(items: List[Dict[str, str]]) -> Dict[str, Any]:
        """items: [{"name": "Home", "item": "https://example.com"}, ...]"""
        item_list = []
        for i, it in enumerate(items):
            item_list.append({
                "@type": "ListItem",
                "position": i + 1,
                "name": it["name"],
                "item": it["item"]
            })
            
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": item_list
        }
    
    @staticmethod
    def organization(name: str, url: str, logo: str, social: List[str] = None) -> Dict[str, Any]:
        """Organization schema for brand recognition"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": name,
            "url": url,
            "logo": logo,
            "sameAs": social or []
        }
    
    @staticmethod
    def local_business(
        name: str,
        address: Dict[str, str],
        phone: str = None,
        image: str = None,
        price_range: str = None,
        opening_hours: List[str] = None
    ) -> Dict[str, Any]:
        """Local business schema for Google Maps"""
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": name,
            "address": {
                "@type": "PostalAddress",
                **address
            },
            "telephone": phone,
            "image": image,
            "priceRange": price_range,
            "openingHours": opening_hours or []
        }
    
    @staticmethod
    def faq(items: List[Dict[str, str]]) -> Dict[str, Any]:
        """FAQ schema for rich results"""
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item["answer"]
                    }
                }
                for item in items
            ]
        }
    
    @staticmethod
    def website(name: str, url: str, search_url: str = None) -> Dict[str, Any]:
        """Website schema with optional sitelinks searchbox"""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": name,
            "url": url
        }
        
        if search_url:
            schema["potentialAction"] = {
                "@type": "SearchAction",
                "target": f"{search_url}?q={{search_term_string}}",
                "query-input": "required name=search_term_string"
            }
        
        return schema
