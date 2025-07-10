const imageFolder = 'images/';
const imageCount = 10;  // Set or dynamically calculate this in a real version

const gallery = document.getElementById('gallery');

for (let i = 1; i <= imageCount; i++) {
  const img = document.createElement('img');
  img.src = `${imageFolder}img${i}.jpg`;
  img.alt = `Image ${i}`;
  gallery.appendChild(img);
}
