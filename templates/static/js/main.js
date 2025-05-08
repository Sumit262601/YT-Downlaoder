const form = document.getElementById('downloadForm');
const statusDiv = document.getElementById('status');
const progressBar = document.getElementById('progressBar');
const progressContainer = document.getElementById('progressBarContainer');
let pollingInterval;

form.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    statusDiv.textContent = "⏬ Starting...";
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';

    fetch('/download', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'started') {
                startPollingProgress();
            } else {
                statusDiv.textContent = data.message;
            }
        });
});

function startPollingProgress() {
    clearInterval(pollingInterval);
    pollingInterval = setInterval(() => {
        fetch('/progress')
            .then(res => res.json())
            .then(data => {
                progressBar.style.width = data.progress + '%';
                statusDiv.textContent = data.message || `⏬ Downloading... ${data.progress}%`;

                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(pollingInterval);
                }
            });
    }, 1000);
}