document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const cloudName = 'dwcsxe3yo'; // Extracted from .env
    const uploadPreset = 'ml_default'; // Standard Cloudinary default for unsigned uploads

    const fields = [
        { id: 'id_hiw_video_embed_seekers', label: 'Job Seekers Video' },
        { id: 'id_hiw_video_embed_employers', label: 'Employers Video' }
    ];

    fields.forEach(field => {
        const input = document.getElementById(field.id);
        if (!input) return;

        // Create the button
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'button';
        btn.innerHTML = '☁️ Upload Video directly to Cloud';
        btn.style.marginTop = '5px';
        btn.style.backgroundColor = '#2ecc71';
        btn.style.color = 'white';
        btn.style.border = 'none';
        btn.style.padding = '5px 15px';
        btn.style.borderRadius = '4px';
        btn.style.cursor = 'pointer';
        btn.style.fontWeight = 'bold';

        // Add button below the input
        input.parentNode.appendChild(btn);

        btn.addEventListener('click', function() {
            cloudinary.openUploadWidget({
                cloudName: cloudName,
                uploadPreset: uploadPreset,
                sources: ['local', 'url', 'camera'],
                resourceType: 'video',
                multiple: false,
                clientAllowedFormats: ['mp4', 'mov', 'avi', 'webm'],
                maxFileSize: 100000000, // 100MB
            }, (error, result) => {
                if (!error && result && result.event === "success") {
                    console.log('Done! Here is the image info: ', result.info);
                    // Put the secure URL into the input field
                    input.value = result.info.secure_url;
                    btn.innerHTML = '✅ Uploaded Successfully!';
                    btn.style.backgroundColor = '#27ae60';
                }
                if (error) {
                    console.error('Upload Error:', error);
                    alert('Cloudinary Error: Make sure you have an "Unsigned" upload preset named "ml_default" enabled in your Cloudinary settings.');
                }
            });
        });
    });
});
