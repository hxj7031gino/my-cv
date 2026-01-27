document.addEventListener('DOMContentLoaded', () => {
    // Page navigation logic
    const navStatement = document.getElementById('nav-statement');
    const navWork = document.getElementById('nav-work');
    const navBiography = document.getElementById('nav-biography');
    const workSection = document.getElementById('work');
    const statementSection = document.getElementById('statement');
    const biographySection = document.getElementById('biography');

    function showWork() {
        workSection.style.display = 'block';
        statementSection.style.display = 'none';
        biographySection.style.display = 'none';
    }

    function showStatement() {
        workSection.style.display = 'none';
        statementSection.style.display = 'block';
        biographySection.style.display = 'none';
    }

    function showBiography() {
        workSection.style.display = 'none';
        statementSection.style.display = 'none';
        biographySection.style.display = 'block';
    }

    navWork.addEventListener('click', (e) => {
        e.preventDefault();
        showWork();
    });

    navStatement.addEventListener('click', (e) => {
        e.preventDefault();
        showStatement();
    });

    navBiography.addEventListener('click', (e) => {
        e.preventDefault();
        showBiography();
    });

    // Initial page state
    showWork();
    
    const galleryGrid = document.querySelector('.gallery-grid');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const closeBtn = document.querySelector('.close-btn');

    const imageFiles = [
        "image1.jpg", "image10.jpg", "image11.jpg", "image12.jpg", "image13.jpg", "image14.JPG", "image15.jpg",
        "image16.jpg", "image17.jpg", "image18.jpg", "image19.jpg", "image2.jpg", "image20.jpg", "image21.jpg",
        "image22.jpg", "image23.jpg", "image24.jpg", "image25.jpg", "image26.jpg", "image27.jpg", "image28.jpg",
        "image29.jpg", "image3.jpg", "image30.jpg", "image31.jpg", "image32.jpg", "image33.jpg", "image34.jpg",
        "image35.jpg", "image36.jpg", "image37.jpg", "image38.jpg", "image39.jpg", "image4.jpg", "image40.jpg",
        "image41.jpg", "image42.jpg", "image43.jpg", "image44.jpg", "image45.jpg", "image46.jpg", "image47.jpg",
        "image48.jpg", "image49.jpg", "image5.jpg", "image50.jpg", "image51.jpg", "image52.jpg", "image53.jpg",
        "image54.jpg", "image55.jpg", "image56.jpg", "image57.jpg", "image58.jpg", "image59.jpg", "image6.jpg",
        "image60.jpg", "image61.JPG", "image62.JPG", "image63.JPG", "image64.JPG", "image65.JPG", "image66.jpg",
        "image67.jpg", "image68.png", "image69.png", "image7.jpg", "image70.png", "image71.png", "image72.png",
        "image73.jpg", "image74.jpg", "image75.jpg", "image76.jpg", "image77.jpg", "image8.jpg", "image9.jpg"
    ];

    // Sort files numerically based on the number in the filename
    imageFiles.sort((a, b) => {
        const numA = parseInt(a.replace(/[^0-9]/g, ''), 10);
        const numB = parseInt(b.replace(/[^0-9]/g, ''), 10);
        return numA - numB;
    });

    // Populate the gallery
    imageFiles.forEach(fileName => {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        
        const img = document.createElement('img');
        img.src = `images/${fileName}`;
        img.loading = 'lazy';
        
        item.appendChild(img);
        galleryGrid.appendChild(item);

        // Add click listener for lightbox
        img.addEventListener('click', () => {
            lightbox.classList.add('active');
            lightboxImg.src = img.src;
        });
    });

    // Close lightbox
    const closeLightbox = () => {
        lightbox.classList.remove('active');
    };

    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
});