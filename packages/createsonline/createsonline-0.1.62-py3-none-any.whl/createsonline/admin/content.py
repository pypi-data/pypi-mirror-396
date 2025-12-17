# createsonline/admin/content.py
"""
CREATESONLINE Content Management

Rich content features inspired by Wagtail:
- Rich text editor
- Image/file upload
- Content versioning (draft/published)
- Content scheduling
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

# Import Base from auth models to avoid foreign key issues
try:
    from createsonline.auth.models import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


# ========================================
# Content Management Models
# ========================================

class ContentVersion(Base):
    """Track content versions for any model"""
    __tablename__ = "createsonline_content_versions"
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(100), nullable=False)  # Model name
    object_id = Column(Integer, nullable=False)
    
    # Version info
    version_number = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)  # Serialized content
    
    # Status
    status = Column(String(20), default='draft')  # draft, published, archived
    
    # User who created this version
    created_by = Column(Integer, ForeignKey('createsonline_users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Publishing
    published_at = Column(DateTime, nullable=True)
    published_by = Column(Integer, ForeignKey('createsonline_users.id'), nullable=True)
    
    # Comment/notes
    comment = Column(Text, nullable=True)


class ScheduledContent(Base):
    """Schedule content for future publishing"""
    __tablename__ = "createsonline_scheduled_content"
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(100), nullable=False)
    object_id = Column(Integer, nullable=False)
    
    # Scheduling
    publish_at = Column(DateTime, nullable=False)
    unpublish_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default='pending')  # pending, published, cancelled
    
    # User who scheduled
    created_by = Column(Integer, ForeignKey('createsonline_users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Execution
    executed_at = Column(DateTime, nullable=True)


class MediaFile(Base):
    """Media file storage"""
    __tablename__ = "createsonline_media_files"
    
    id = Column(Integer, primary_key=True)
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)  # image, document, video, etc.
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    
    # Image-specific
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Metadata
    title = Column(String(255), nullable=True)
    alt_text = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Upload info
    uploaded_by = Column(Integer, ForeignKey('createsonline_users.id'))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)


# ========================================
# Rich Text Field
# ========================================

class RichTextField:
    """
    Rich text field for models
    
    Provides:
    - HTML editor
    - Markdown support
    - Media embedding
    - Link management
    """
    
    def __init__(self, allow_html: bool = True, allow_markdown: bool = True):
        self.allow_html = allow_html
        self.allow_markdown = allow_markdown
    
    def render_editor(self, field_name: str, value: str = "", field_id: str = None) -> str:
        """Render rich text editor HTML"""
        field_id = field_id or field_name
        
        # Simple rich text editor with toolbar
        html = f"""
<div class="rich-text-editor">
    <div class="editor-toolbar">
        <button type="button" class="editor-btn" data-action="bold" title="Bold">
            <strong>B</strong>
        </button>
        <button type="button" class="editor-btn" data-action="italic" title="Italic">
            <em>I</em>
        </button>
        <button type="button" class="editor-btn" data-action="underline" title="Underline">
            <u>U</u>
        </button>
        <span class="toolbar-separator"></span>
        <button type="button" class="editor-btn" data-action="h1" title="Heading 1">H1</button>
        <button type="button" class="editor-btn" data-action="h2" title="Heading 2">H2</button>
        <button type="button" class="editor-btn" data-action="h3" title="Heading 3">H3</button>
        <span class="toolbar-separator"></span>
        <button type="button" class="editor-btn" data-action="ul" title="Bullet List">• List</button>
        <button type="button" class="editor-btn" data-action="ol" title="Numbered List">1. List</button>
        <span class="toolbar-separator"></span>
        <button type="button" class="editor-btn" data-action="link" title="Insert Link"></button>
        <button type="button" class="editor-btn" data-action="image" title="Insert Image">🖼</button>
        <span class="toolbar-separator"></span>
        <button type="button" class="editor-btn" data-action="code" title="Code Block">&lt;/&gt;</button>
        <button type="button" class="editor-btn" data-action="quote" title="Quote">" "</button>
    </div>
    <div class="editor-content" contenteditable="true" id="{field_id}_editor">{value}</div>
    <textarea name="{field_name}" id="{field_id}" style="display: none;">{value}</textarea>
</div>

<style>
.rich-text-editor {{
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    overflow: hidden;
}}

.editor-toolbar {{
    background: #0a0a0a;
    padding: 8px;
    border-bottom: 1px solid #3a3a3a;
    display: flex;
    gap: 4px;
    align-items: center;
}}

.editor-btn {{
    padding: 6px 10px;
    background: #2a2a2a;
    color: #ffffff;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
}}

.editor-btn:hover {{
    background: #3a3a3a;
}}

.editor-btn:active {{
    background: #4a4a4a;
}}

.toolbar-separator {{
    width: 1px;
    height: 20px;
    background: #3a3a3a;
    margin: 0 4px;
}}

.editor-content {{
    min-height: 200px;
    padding: 15px;
    background: #1a1a1a;
    color: #ffffff;
    outline: none;
}}

.editor-content:focus {{
    background: #1a1a1a;
}}

/* Content styles */
.editor-content h1 {{
    font-size: 2em;
    margin: 0.5em 0;
}}

.editor-content h2 {{
    font-size: 1.5em;
    margin: 0.5em 0;
}}

.editor-content h3 {{
    font-size: 1.25em;
    margin: 0.5em 0;
}}

.editor-content ul, .editor-content ol {{
    margin: 0.5em 0;
    padding-left: 2em;
}}

.editor-content blockquote {{
    border-left: 3px solid #3a3a3a;
    padding-left: 1em;
    margin: 1em 0;
    color: #b0b0b0;
}}

.editor-content code {{
    background: #0a0a0a;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}}

.editor-content pre {{
    background: #0a0a0a;
    padding: 15px;
    border-radius: 8px;
    overflow-x: auto;
}}

.editor-content a {{
    color: #ffffff;
    text-decoration: underline;
}}

.editor-content img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}}
</style>

<script>
(function() {{
    const editor = document.getElementById('{field_id}_editor');
    const textarea = document.getElementById('{field_id}');
    
    // Sync editor content to textarea
    editor.addEventListener('input', function() {{
        textarea.value = editor.innerHTML;
    }});
    
    // Toolbar actions
    document.querySelectorAll('.editor-btn').forEach(btn => {{
        btn.addEventListener('click', function(e) {{
            e.preventDefault();
            const action = this.dataset.action;
            
            switch(action) {{
                case 'bold':
                    document.execCommand('bold');
                    break;
                case 'italic':
                    document.execCommand('italic');
                    break;
                case 'underline':
                    document.execCommand('underline');
                    break;
                case 'h1':
                    document.execCommand('formatBlock', false, 'h1');
                    break;
                case 'h2':
                    document.execCommand('formatBlock', false, 'h2');
                    break;
                case 'h3':
                    document.execCommand('formatBlock', false, 'h3');
                    break;
                case 'ul':
                    document.execCommand('insertUnorderedList');
                    break;
                case 'ol':
                    document.execCommand('insertOrderedList');
                    break;
                case 'link':
                    const url = prompt('Enter URL:');
                    if (url) document.execCommand('createLink', false, url);
                    break;
                case 'image':
                    const imgUrl = prompt('Enter image URL:');
                    if (imgUrl) document.execCommand('insertImage', false, imgUrl);
                    break;
                case 'code':
                    document.execCommand('formatBlock', false, 'pre');
                    break;
                case 'quote':
                    document.execCommand('formatBlock', false, 'blockquote');
                    break;
            }}
            
            editor.focus();
        }});
    }});
}})();
</script>
"""
        return html


# ========================================
# Image Upload Field
# ========================================

class ImageField:
    """
    Image upload field
    
    Provides:
    - File upload
    - Image preview
    - Validation
    - Resize options
    """
    
    def __init__(
        self,
        max_size_mb: float = 5.0,
        allowed_formats: List[str] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ):
        self.max_size_mb = max_size_mb
        self.allowed_formats = allowed_formats or ['jpg', 'jpeg', 'png', 'gif', 'webp']
        self.max_width = max_width
        self.max_height = max_height
    
    def render_uploader(self, field_name: str, current_value: str = "", field_id: str = None) -> str:
        """Render image upload field"""
        field_id = field_id or field_name
        
        preview_html = ""
        if current_value:
            preview_html = f'<img src="{current_value}" alt="Current image" class="image-preview">'
        
        html = f"""
<div class="image-upload-field">
    <div class="upload-area" id="{field_id}_upload_area">
        {preview_html}
        <div class="upload-prompt">
            <span class="upload-icon"></span>
            <p>Click to upload or drag and drop</p>
            <p class="upload-hint">
                Max {self.max_size_mb}MB • {', '.join(self.allowed_formats).upper()}
            </p>
        </div>
    </div>
    <input type="file" name="{field_name}" id="{field_id}" accept="image/*" style="display: none;">
    <input type="hidden" name="{field_name}_url" id="{field_id}_url" value="{current_value}">
</div>

<style>
.image-upload-field {{
    border: 2px dashed #3a3a3a;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
}}

.image-upload-field:hover {{
    border-color: #ffffff;
    background: #1a1a1a;
}}

.upload-area {{
    position: relative;
}}

.image-preview {{
    max-width: 100%;
    max-height: 300px;
    border-radius: 8px;
    margin-bottom: 15px;
}}

.upload-icon {{
    font-size: 3em;
    display: block;
    margin-bottom: 10px;
}}

.upload-prompt p {{
    color: #b0b0b0;
    margin: 5px 0;
}}

.upload-hint {{
    font-size: 0.85em;
    color: #888;
}}
</style>

<script>
(function() {{
    const uploadArea = document.getElementById('{field_id}_upload_area');
    const fileInput = document.getElementById('{field_id}');
    const urlInput = document.getElementById('{field_id}_url');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', function(e) {{
        const file = e.target.files[0];
        if (file) {{
            // Validate file size
            if (file.size > {self.max_size_mb} * 1024 * 1024) {{
                alert('File too large! Max {self.max_size_mb}MB');
                return;
            }}
            
            // Validate file type
            const ext = file.name.split('.').pop().toLowerCase();
            const allowed = {self.allowed_formats};
            if (!allowed.includes(ext)) {{
                alert('Invalid file type! Allowed: ' + allowed.join(', '));
                return;
            }}
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {{
                uploadArea.innerHTML = '<img src="' + e.target.result + '" class="image-preview">';
                urlInput.value = e.target.result;
            }};
            reader.readAsDataURL(file);
        }}
    }});
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {{
        e.preventDefault();
        uploadArea.style.borderColor = '#ffffff';
    }});
    
    uploadArea.addEventListener('dragleave', () => {{
        uploadArea.style.borderColor = '#3a3a3a';
    }});
    
    uploadArea.addEventListener('drop', (e) => {{
        e.preventDefault();
        uploadArea.style.borderColor = '#3a3a3a';
        
        const file = e.dataTransfer.files[0];
        if (file) {{
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }}
    }});
}})();
</script>
"""
        return html


# ========================================
# Content Status Mixin
# ========================================

class ContentStatusMixin:
    """Mixin to add content status to models"""
    
    status = Column(String(20), default='draft')  # draft, published, archived
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def publish(self):
        """Publish content"""
        self.status = 'published'
        self.published_at = datetime.utcnow()
    
    def unpublish(self):
        """Unpublish content"""
        self.status = 'draft'
        self.published_at = None
    
    def archive(self):
        """Archive content"""
        self.status = 'archived'
    
    @property
    def is_published(self) -> bool:
        """Check if content is published"""
        return self.status == 'published'
    
    @property
    def is_draft(self) -> bool:
        """Check if content is draft"""
        return self.status == 'draft'
