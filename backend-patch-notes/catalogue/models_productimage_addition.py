"""
ADDITIVE field + save() override for catalogue/models.py ProductImage
class. Add the field to the class body, and add the save() method
(ProductImage currently has no custom save()). Existing images keep
fit_mode='cover' (the default) and are otherwise untouched; the resize
logic only runs on NEW saves, so already-uploaded images on the server
are not reprocessed or altered.
"""
PRODUCTIMAGE_ADDITIONS = '''
    FIT_CHOICES = [("cover", "Fill and crop (cover)"), ("contain", "Fit whole image (contain)")]
    fit_mode = models.CharField(
        max_length=10, choices=FIT_CHOICES, default="cover",
        help_text="How this image fits its frame on the site. \\'Cover\\' fills the "
                  "space and crops edges; \\'Contain\\' shows the whole image with "
                  "letterboxing. Choose \\'Contain\\' for logos or images that must not be cropped.")

    def save(self, *args, **kwargs):
        # Constrain very large uploads so the site never serves an
        # unnecessarily huge file; preserves aspect ratio, does not crop.
        if self.image and hasattr(self.image, "file"):
            from PIL import Image
            from io import BytesIO
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import sys
            try:
                img = Image.open(self.image)
                max_dim = 1600
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
                    buffer = BytesIO()
                    fmt = "JPEG" if img.mode in ("RGB", "L") else "PNG"
                    if fmt == "JPEG" and img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(buffer, format=fmt, quality=88, optimize=True)
                    buffer.seek(0)
                    self.image = InMemoryUploadedFile(
                        buffer, "ImageField", self.image.name, f"image/{fmt.lower()}",
                        sys.getsizeof(buffer), None)
            except Exception:
                pass  # if Pillow can't process it, save the original untouched
        super().save(*args, **kwargs)
'''
print(PRODUCTIMAGE_ADDITIONS)
