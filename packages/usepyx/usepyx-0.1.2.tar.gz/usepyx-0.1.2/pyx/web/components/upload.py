"""
PyX File Upload Component
Handle file uploads with progress tracking.
"""
import os
import secrets
from typing import Optional, List
from datetime import datetime


class FileUpload:
    """
    File upload handler for PyX.
    
    Usage:
        from pyx.components import FileUpload
        
        # In your route handler, use FastAPI's file upload:
        @app.api.post("/upload")
        async def upload(file: UploadFile):
            result = await FileUpload.save(file, "uploads/")
            return result
    """
    
    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB default
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "txt", "csv"]
    
    @classmethod
    def configure(
        cls,
        upload_dir: str = "uploads",
        max_size: int = 10 * 1024 * 1024,
        allowed_extensions: List[str] = None
    ):
        """
        Configure upload settings.
        
        Args:
            upload_dir: Directory to save files
            max_size: Maximum file size in bytes
            allowed_extensions: List of allowed file extensions
        """
        cls.UPLOAD_DIR = upload_dir
        cls.MAX_FILE_SIZE = max_size
        if allowed_extensions:
            cls.ALLOWED_EXTENSIONS = allowed_extensions
        
        # Ensure directory exists
        os.makedirs(upload_dir, exist_ok=True)
    
    @classmethod
    def _generate_filename(cls, original_name: str) -> str:
        """Generate a unique filename"""
        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
        unique = secrets.token_hex(8)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{unique}.{ext}" if ext else f"{timestamp}_{unique}"
    
    @classmethod
    def _validate_extension(cls, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not cls.ALLOWED_EXTENSIONS:
            return True
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    async def save(
        cls,
        file,  # UploadFile from FastAPI
        subdir: str = "",
        custom_name: str = None
    ) -> dict:
        """
        Save uploaded file.
        
        Args:
            file: FastAPI UploadFile object
            subdir: Subdirectory within upload dir
            custom_name: Custom filename (optional)
            
        Returns:
            dict with file info: {success, filename, path, size, error}
        """
        try:
            # Validate extension
            if not cls._validate_extension(file.filename):
                return {
                    "success": False,
                    "error": f"File type not allowed. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
                }
            
            # Read file content
            content = await file.read()
            
            # Check file size
            if len(content) > cls.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "error": f"File too large. Maximum size: {cls.MAX_FILE_SIZE // (1024*1024)}MB"
                }
            
            # Generate filename
            filename = custom_name if custom_name else cls._generate_filename(file.filename)
            
            # Create full path
            save_dir = os.path.join(cls.UPLOAD_DIR, subdir) if subdir else cls.UPLOAD_DIR
            os.makedirs(save_dir, exist_ok=True)
            
            filepath = os.path.join(save_dir, filename)
            
            # Save file
            with open(filepath, "wb") as f:
                f.write(content)
            
            return {
                "success": True,
                "filename": filename,
                "original_name": file.filename,
                "path": filepath,
                "size": len(content),
                "url": f"/uploads/{subdir}/{filename}" if subdir else f"/uploads/{filename}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @classmethod
    def delete(cls, filepath: str) -> bool:
        """Delete an uploaded file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except:
            return False
    
    @classmethod
    def get_ui_script(cls) -> str:
        """
        Returns JavaScript for file upload with progress tracking.
        Include this in your page for enhanced upload experience.
        """
        return '''
        <script>
        // PyX File Upload Helper
        PyX.upload = {
            // Upload file with progress tracking
            uploadFile: function(inputId, url, options = {}) {
                const input = document.getElementById(inputId);
                if (!input || !input.files || !input.files[0]) {
                    PyX.toast('Please select a file', 'error');
                    return Promise.reject('No file selected');
                }
                
                const file = input.files[0];
                const formData = new FormData();
                formData.append('file', file);
                
                // Add extra fields
                if (options.extraData) {
                    Object.keys(options.extraData).forEach(key => {
                        formData.append(key, options.extraData[key]);
                    });
                }
                
                return new Promise((resolve, reject) => {
                    const xhr = new XMLHttpRequest();
                    
                    // Progress tracking
                    if (options.onProgress) {
                        xhr.upload.addEventListener('progress', (e) => {
                            if (e.lengthComputable) {
                                const percent = Math.round((e.loaded / e.total) * 100);
                                options.onProgress(percent, e.loaded, e.total);
                            }
                        });
                    }
                    
                    xhr.addEventListener('load', () => {
                        if (xhr.status >= 200 && xhr.status < 300) {
                            const result = JSON.parse(xhr.responseText);
                            PyX.toast('File uploaded successfully', 'success');
                            resolve(result);
                        } else {
                            PyX.toast('Upload failed', 'error');
                            reject(xhr.responseText);
                        }
                    });
                    
                    xhr.addEventListener('error', () => {
                        PyX.toast('Upload error', 'error');
                        reject('Network error');
                    });
                    
                    xhr.open('POST', url);
                    xhr.send(formData);
                });
            },
            
            // Create file input with preview
            createInput: function(id, options = {}) {
                const accept = options.accept || '*/*';
                const multiple = options.multiple ? 'multiple' : '';
                
                return `
                    <div class="pyx-file-input" id="${id}-container">
                        <input type="file" id="${id}" accept="${accept}" ${multiple} 
                            class="hidden" onchange="PyX.upload.handlePreview('${id}')">
                        <label for="${id}" 
                            class="flex flex-col items-center justify-center w-full h-32 
                                   border-2 border-dashed border-gray-300 rounded-lg 
                                   cursor-pointer hover:border-blue-500 hover:bg-gray-50 transition">
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                            </svg>
                            <span class="mt-2 text-sm text-gray-500">Click to upload or drag and drop</span>
                        </label>
                        <div id="${id}-preview" class="mt-2 hidden">
                            <div class="flex items-center gap-2 p-2 bg-gray-100 rounded">
                                <span id="${id}-filename" class="text-sm text-gray-700"></span>
                                <button onclick="PyX.upload.clearInput('${id}')" class="text-red-500 text-sm">✕</button>
                            </div>
                        </div>
                        <div id="${id}-progress" class="mt-2 hidden">
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div id="${id}-progress-bar" class="bg-blue-600 h-2 rounded-full" style="width: 0%"></div>
                            </div>
                            <span id="${id}-progress-text" class="text-xs text-gray-500">0%</span>
                        </div>
                    </div>
                `;
            },
            
            handlePreview: function(id) {
                const input = document.getElementById(id);
                const preview = document.getElementById(id + '-preview');
                const filename = document.getElementById(id + '-filename');
                
                if (input.files && input.files[0]) {
                    filename.textContent = input.files[0].name;
                    preview.classList.remove('hidden');
                }
            },
            
            clearInput: function(id) {
                const input = document.getElementById(id);
                const preview = document.getElementById(id + '-preview');
                input.value = '';
                preview.classList.add('hidden');
            },
            
            showProgress: function(id, percent) {
                const progress = document.getElementById(id + '-progress');
                const bar = document.getElementById(id + '-progress-bar');
                const text = document.getElementById(id + '-progress-text');
                
                progress.classList.remove('hidden');
                bar.style.width = percent + '%';
                text.textContent = percent + '%';
            }
        };
        </script>
        '''


# Convenience alias
upload = FileUpload
