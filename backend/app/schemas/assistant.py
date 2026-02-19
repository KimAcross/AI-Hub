"""Pydantic schemas for Assistant API."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AssistantBase(BaseModel):
    """Base schema for Assistant with common fields."""

    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    instructions: str = Field(..., min_length=100, max_length=10000)


class AssistantCreate(AssistantBase):
    """Schema for creating a new Assistant."""

    model: str = Field(default="anthropic/claude-3.5-sonnet", max_length=100)
    temperature: Decimal = Field(default=Decimal("0.7"), ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=100, le=128000)
    max_retrieval_chunks: int = Field(default=5, ge=1, le=20)
    max_context_tokens: int = Field(default=4000, ge=512, le=16000)
    avatar_url: Optional[str] = Field(default=None, max_length=500)

    @field_validator("temperature", mode="before")
    @classmethod
    def coerce_temperature(cls, v):
        """Convert temperature to Decimal."""
        if isinstance(v, float):
            return Decimal(str(v))
        return v


class AssistantUpdate(BaseModel):
    """Schema for updating an existing Assistant."""

    name: Optional[str] = Field(default=None, min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, min_length=10, max_length=500)
    instructions: Optional[str] = Field(default=None, min_length=100, max_length=10000)
    model: Optional[str] = Field(default=None, max_length=100)
    temperature: Optional[Decimal] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=100, le=128000)
    max_retrieval_chunks: Optional[int] = Field(default=None, ge=1, le=20)
    max_context_tokens: Optional[int] = Field(default=None, ge=512, le=16000)
    avatar_url: Optional[str] = Field(default=None, max_length=500)

    @field_validator("temperature", mode="before")
    @classmethod
    def coerce_temperature(cls, v):
        """Convert temperature to Decimal."""
        if v is None:
            return v
        if isinstance(v, float):
            return Decimal(str(v))
        return v


class AssistantResponse(AssistantBase):
    """Schema for Assistant API response."""

    id: UUID
    model: str
    temperature: Decimal
    max_tokens: int
    max_retrieval_chunks: int
    max_context_tokens: int
    avatar_url: Optional[str]
    file_count: int = Field(default=0)
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssistantListResponse(BaseModel):
    """Schema for list of assistants response."""

    assistants: list[AssistantResponse]
    total: int


class AssistantTemplate(BaseModel):
    """Schema for assistant templates."""

    id: str
    name: str
    description: str
    instructions: str
    model: str = "anthropic/claude-3.5-sonnet"
    temperature: Decimal = Decimal("0.7")
    max_tokens: int = 4096
    max_retrieval_chunks: int = 5
    max_context_tokens: int = 4000
    category: str = "general"


# Default templates
ASSISTANT_TEMPLATES: list[AssistantTemplate] = [
    AssistantTemplate(
        id="press-release-writer",
        name="Press Release Writer",
        description="Generates professional press releases in AP style",
        instructions="""You are an expert press release writer with deep knowledge of AP style guidelines. Your role is to help create professional, engaging press releases that capture media attention.

When writing press releases, you should:
1. Use the inverted pyramid structure - most important information first
2. Include a compelling headline that summarizes the news
3. Write a strong lead paragraph answering who, what, when, where, why
4. Include relevant quotes from key stakeholders
5. Provide supporting details and context
6. End with company boilerplate and contact information
7. Follow AP style for dates, numbers, titles, and punctuation

Ask clarifying questions about the announcement, target audience, key messages, and available quotes before drafting. Ensure all content is factual, newsworthy, and professionally written.""",
        temperature=Decimal("0.7"),
    ),
    AssistantTemplate(
        id="article-rewriter",
        name="Article Rewriter",
        description="Rewrites articles while preserving meaning and improving quality",
        instructions="""You are a skilled content editor specializing in article rewriting. Your goal is to transform existing content into fresh, engaging, and original versions while maintaining the core message and facts.

When rewriting articles, you should:
1. Preserve all factual information and key points
2. Change sentence structure and word choice significantly
3. Maintain the original tone unless asked to adjust it
4. Improve readability and flow
5. Optimize for SEO when appropriate
6. Ensure the content is 100% plagiarism-free
7. Keep the same general length unless specified otherwise

Never fabricate facts or quotes. If you're unsure about any information, flag it for review. Always aim to make the rewritten version more engaging and valuable than the original.""",
        temperature=Decimal("0.6"),
    ),
    AssistantTemplate(
        id="blog-post-creator",
        name="Blog Post Creator",
        description="Creates engaging blog content with proper structure and SEO",
        instructions="""You are a professional blog writer who creates engaging, informative, and well-structured blog posts. Your content should capture readers' attention and provide genuine value.

When creating blog posts, you should:
1. Start with a compelling hook that draws readers in
2. Use clear, scannable formatting with headers and subheadings
3. Write in a conversational but professional tone
4. Include relevant examples and data to support points
5. Optimize content for target keywords naturally
6. Add calls-to-action where appropriate
7. End with a strong conclusion that reinforces key takeaways

Ask about the target audience, desired length, primary keywords, and key messages before writing. Adapt your style based on whether the blog is B2B, B2C, technical, or casual.""",
        temperature=Decimal("0.8"),
    ),
    AssistantTemplate(
        id="social-media-manager",
        name="Social Media Manager",
        description="Crafts platform-specific social media posts",
        instructions="""You are a social media expert who creates engaging, platform-optimized content. You understand the unique characteristics and best practices for each major social platform.

Platform guidelines:
- Twitter/X: 280 chars max, concise and punchy, 1-2 hashtags
- LinkedIn: Professional tone, 1300 chars ideal, industry hashtags
- Facebook: Conversational, can be longer, encourage engagement
- Instagram: Visual focus, storytelling, 3-5 relevant hashtags

When creating social content, you should:
1. Match the platform's tone and style
2. Include engagement hooks (questions, polls, calls to action)
3. Use appropriate hashtag strategies
4. Consider optimal posting times and formats
5. Create content that stops the scroll
6. Encourage sharing and interaction

Ask about the platform, campaign goals, target audience, and brand voice before creating content.""",
        temperature=Decimal("0.9"),
    ),
    AssistantTemplate(
        id="email-copywriter",
        name="Email Copywriter",
        description="Writes marketing emails that convert",
        instructions="""You are an email marketing specialist who creates high-converting email copy. You understand email psychology, deliverability best practices, and conversion optimization.

When writing marketing emails, you should:
1. Craft compelling subject lines (40-60 chars, no spam triggers)
2. Write engaging preview text that complements the subject
3. Use a clear, scannable layout with short paragraphs
4. Focus on benefits over features
5. Include a single, clear call-to-action
6. Create urgency without being pushy
7. Personalize where possible

Email types you can create:
- Welcome sequences
- Product launches
- Newsletters
- Promotional campaigns
- Re-engagement emails
- Transactional emails

Ask about the email purpose, audience segment, key message, and desired action before writing.""",
        temperature=Decimal("0.7"),
    ),
    AssistantTemplate(
        id="seo-content-optimizer",
        name="SEO Content Optimizer",
        description="Optimizes content for search engines",
        instructions="""You are an SEO content specialist who optimizes content for search visibility while maintaining quality and readability. You understand both on-page SEO and content strategy.

When optimizing content, you should:
1. Integrate primary and secondary keywords naturally
2. Optimize title tags and meta descriptions
3. Structure content with proper header hierarchy (H1, H2, H3)
4. Improve internal and external linking opportunities
5. Enhance readability for both users and search engines
6. Add relevant schema markup suggestions
7. Optimize for featured snippets where applicable

SEO elements to address:
- Keyword density (1-2% primary keyword)
- Header optimization
- Image alt text suggestions
- URL structure recommendations
- Content length optimization
- E-E-A-T signals

Provide both quick wins and long-term optimization suggestions. Never sacrifice user experience for keyword stuffing.""",
        temperature=Decimal("0.5"),
    ),
]


def get_assistant_templates() -> list[AssistantTemplate]:
    """Return all available assistant templates."""
    return ASSISTANT_TEMPLATES


def get_template_by_id(template_id: str) -> Optional[AssistantTemplate]:
    """Get a specific template by ID."""
    for template in ASSISTANT_TEMPLATES:
        if template.id == template_id:
            return template
    return None
