// Wait for the HTML to be fully loaded before running any script
document.addEventListener('DOMContentLoaded', () => {
    
    // We create a single 'App' object to hold everything.
    // This keeps our code clean and organized.
    const App = {
        // 1. STATE: Store changing variables here
        state: {
            currentStream: null,
        },

        // 2. ELEMENTS: Store all our DOM elements here
        elements: {},

        // 3. INIT: This function runs first. Its job is to find
        // all the elements and set up the event listeners.
        init() {
            // Find and store all elements
            this.elements.fileInput = document.getElementById('fileInput');
            this.elements.imagePreview = document.getElementById('imagePreview');
            this.elements.videoStream = document.getElementById('videoStream');
            this.elements.captureCanvas = document.getElementById('captureCanvas');
            this.elements.previewContainer = document.getElementById('preview');
            this.elements.cameraButton = document.getElementById('cameraButton');
            this.elements.captureButton = document.getElementById('captureButton');
            this.elements.extractButton = document.getElementById('extractButton');
            this.elements.clearButton = document.getElementById('clearButton');
            this.elements.statusDiv = document.getElementById('status');
            this.elements.outputDiv = document.getElementById('output');
            this.elements.resultTextarea = document.getElementById('resultTextarea');
            this.elements.copyButton = document.getElementById('copyButton');
            this.elements.customModal = document.getElementById('custom-modal');
            this.elements.modalTitle = document.getElementById('modal-title');
            this.elements.modalMessage = document.getElementById('modal-message');
            this.elements.modalCloseBtn = document.getElementById('modal-close-btn');
            this.elements.totalContainer = document.getElementById('totalContainer');
            this.elements.finalTotalInput = document.getElementById('finalTotalInput');
            this.elements.saveButton = document.getElementById('saveButton');
            this.elements.extractTotalButton = document.getElementById('extractTotalButton');

            // Set up all event listeners
            this.setupEventListeners();
            
            // Set the initial state of the app
            this.clearUI();
        },

        // 4. EVENT LISTENERS: All listeners are organized in one place.
        setupEventListeners() {
            // We use .bind(this) to make sure that 'this' inside the
            // function refers to the 'App' object.
            this.elements.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
            this.elements.cameraButton.addEventListener('click', this.startCamera.bind(this));
            this.elements.captureButton.addEventListener('click', this.captureImage.bind(this));
            this.elements.extractButton.addEventListener('click', this.extractText.bind(this));
            this.elements.clearButton.addEventListener('click', this.clearUI.bind(this));
            this.elements.copyButton.addEventListener('click', this.copyText.bind(this));
            this.elements.extractTotalButton.addEventListener('click', this.findTotal.bind(this));
            this.elements.saveButton.addEventListener('click', this.saveTotal.bind(this));
            this.elements.modalCloseBtn.addEventListener('click', this.handleModelConfirm.bind(this));
        },

        // 5. METHODS: These are all the functions that make the app work.
        // Each function has one clear job.

        handleFileSelect(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                this.elements.imagePreview.src = event.target.result;
                this.elements.previewContainer.classList.remove('hidden');
                this.elements.imagePreview.classList.remove('hidden');
                this.elements.videoStream.classList.add('hidden');
                this.elements.statusDiv.textContent = 'Image loaded. Click "Extract Text".';
                this.elements.outputDiv.classList.add('hidden');
                this.elements.totalContainer.classList.remove('hidden');
                this.elements.extractButton.disabled = false;
            };
            reader.readAsDataURL(file);
        },

        async startCamera() {
            this.clearUI();
            this.elements.previewContainer.classList.remove('hidden');
            this.elements.videoStream.classList.remove('hidden');
            this.elements.imagePreview.classList.add('hidden');
            this.elements.captureButton.classList.remove('hidden');
            this.elements.fileInput.disabled = true;

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' } 
                });
                this.elements.videoStream.srcObject = stream;
                this.state.currentStream = stream;
                this.elements.statusDiv.textContent = 'Camera is live. Click "Capture".';
            } catch (err) {
                console.error('Error accessing camera:', err);
                this.showModal('Camera Error', 'Could not access the camera. Please grant permissions.');
                this.stopCamera();
            }
        },

        captureImage() {
            if (!this.state.currentStream) {
                this.showModal('Error', 'No camera stream available.');
                return;
            }
            const video = this.elements.videoStream;
            const canvas = this.elements.captureCanvas;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

            this.stopCamera();

            this.elements.imagePreview.src = canvas.toDataURL('image/png');
            this.elements.imagePreview.classList.remove('hidden');
            this.elements.statusDiv.textContent = 'Image captured. Click "Extract Text".';
            this.elements.extractButton.disabled = false;
        },

        async extractText() {
            let imageToProcess = this.elements.imagePreview.src;

            if (!imageToProcess || this.elements.imagePreview.classList.contains('hidden')) {
                this.showModal('Error', 'Please select an image or capture one first.');
                return;
            }

            this.elements.extractButton.disabled = true;
            this.elements.statusDiv.textContent = 'Processing... (0%)';

            try {
                const { data: { text } } = await Tesseract.recognize(
                    imageToProcess,
                    'eng',
                    { 
                        logger: m => {
                            if (m.status === 'recognizing text') {
                                this.elements.statusDiv.textContent = `Processing... (${(m.progress * 100).toFixed(0)}%)`;
                            }
                        }
                    }
                );
                this.elements.resultTextarea.value = text;
                this.elements.outputDiv.classList.remove('hidden');
                this.elements.statusDiv.textContent = 'Extraction complete!';
            } catch (error) {
                console.error(error);
                this.elements.statusDiv.textContent = 'Error during extraction.';
                this.showModal('Error', 'An error occurred during text extraction.');
            } finally {
                this.elements.extractButton.disabled = false;
            }
        },

        clearUI() {
            this.stopCamera();
            this.elements.fileInput.value = '';
            this.elements.fileInput.disabled = false;
            this.elements.imagePreview.src = '';
            this.elements.previewContainer.classList.add('hidden');
            this.elements.outputDiv.classList.add('hidden');
            this.elements.totalContainer.classList.add('remove');
            this.elements.finalTotalInput.value = '';
            this.elements.statusDiv.textContent = 'Please select an image or use your camera. If you wish to enter a spesific amount, please type it below';
            this.elements.extractButton.disabled = true;
            this.elements.captureButton.classList.add('hidden');
        },

        stopCamera() {
            if (this.state.currentStream) {
                this.state.currentStream.getTracks().forEach(track => track.stop());
                this.state.currentStream = null;
            }
            this.elements.videoStream.classList.add('hidden');
            this.elements.captureButton.classList.add('hidden');
            this.elements.fileInput.disabled = false;
        },

        copyText() {
            const textToCopy = this.elements.resultTextarea.value;
            if (!textToCopy) {
                this.showModal('Nothing to Copy', 'The text area is empty.');
                return;
            }
            navigator.clipboard.writeText(textToCopy).then(() => {
                this.showModal('Success', 'Text copied to clipboard!');
            }).catch(err => {
                this.showModal('Error', 'Failed to copy text.');
            });
        },

        findTotal() {
            const extractedText = this.elements.resultTextarea.value.trim();
            if (!extractedText) {
                this.showModal("Error", "Please extract text first.");
                return;
            }
            
            this.elements.totalContainer.classList.remove('hidden');
            this.elements.finalTotalInput.value = '';

            const lines = extractedText.split("\n");
            const totalLine = lines.find(line => 
                line.includes("RM") || /total/i.test(line)
            );

            if (totalLine) {
                const numberMatch = totalLine.match(/(\d+\.\d{2}|\d+)(?!.*\d)/);
                if (numberMatch && numberMatch[0]) {
                    const finalAmount = parseFloat(numberMatch[0]).toFixed(2);
                    this.elements.finalTotalInput.value = finalAmount;
                    this.showModal("Total Extracted!", `We found an amount: <strong>RM ${finalAmount}</strong>.`);
                } else {
                    this.showModal("Total Not Found", "We found a relevant line but couldn't get a number. Please enter it manually.");
                }
            } else {
                this.showModal("Total Not Found", "No line with 'RM' or 'Total' found. Please enter it manually.");
            }
        },

        saveTotal() {
            const finalValue = this.elements.finalTotalInput.value;
            if (finalValue && parseFloat(finalValue) > 0) {
                this.showModal("Final Total Saved", `The final total is <strong>RM ${parseFloat(finalValue).toFixed(2)}</strong>.`);
                // In a real app, you would send this value to a database.
            } else {
                this.showModal("Invalid Amount", "Please enter a valid amount.");
            }
        },

        showModal(title, message) {
            this.elements.modalTitle.textContent = title;
            this.elements.modalMessage.innerHTML = message; // Use innerHTML for <strong>
            this.elements.customModal.classList.remove('hidden');
        },

        handleModelConfirm() {
        this.hideModal();
        this.NextPage();
        },

        NextPage() {
            console.log("Bring to next page")
        },

        hideModal() {
            this.elements.customModal.classList.add('hidden');
        }
    };

    // This is the line that starts the whole app
    App.init();
});