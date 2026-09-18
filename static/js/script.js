let recognition;
let isRecording = false;
let isTranslating = false;


function initializeSpeechRecognition() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        alert(
            "Speech recognition is not supported. Please use Google Chrome."
        );

        return false;
    }

    recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-IN";


    recognition.onstart = function () {

        isRecording = true;

        const recordButton =
            document.getElementById("recordButton");

        const recordText =
            document.getElementById("recordText");

        const status =
            document.getElementById("recordingStatus");

        if (recordButton) {
            recordButton.classList.add("recording");
        }

        if (recordText) {
            recordText.innerText = "Listening...";
        }

        if (status) {
            status.innerText = "Listening";
            status.classList.add("active");
        }
    };


    recognition.onresult = function (event) {

        let finalTranscript = "";
        let interimTranscript = "";

        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {

            const transcript =
                event.results[i][0].transcript;

            if (event.results[i].isFinal) {

                finalTranscript += transcript;

            } else {

                interimTranscript += transcript;
            }
        }

        const inputText =
            document.getElementById("inputText");

        if (inputText) {

            if (finalTranscript) {

                inputText.value +=
                    finalTranscript + " ";
            }

            if (interimTranscript) {

                inputText.placeholder =
                    interimTranscript;
            }
        }
    };


    recognition.onerror = function (event) {

        console.log(
            "Speech recognition error:",
            event.error
        );

        stopRecording();

        if (event.error === "not-allowed") {

            alert(
                "Please allow microphone access."
            );
        }
    };


    recognition.onend = function () {

        stopRecording();
    };


    return true;
}


function startRecording() {

    if (isRecording) {

        recognition.stop();

        return;
    }


    if (!recognition) {

        const initialized =
            initializeSpeechRecognition();

        if (!initialized) {
            return;
        }
    }


    const sourceLanguage =
        document.getElementById(
            "sourceLanguage"
        ).value;


    if (sourceLanguage !== "auto") {

        recognition.lang =
            getSpeechRecognitionLanguage(
                sourceLanguage
            );

    } else {

        recognition.lang = "en-IN";
    }


    try {

        recognition.start();

    } catch (error) {

        console.log(error);
    }
}


function stopRecording() {

    isRecording = false;

    const recordButton =
        document.getElementById("recordButton");

    const recordText =
        document.getElementById("recordText");

    const status =
        document.getElementById("recordingStatus");


    if (recordButton) {

        recordButton.classList.remove(
            "recording"
        );
    }


    if (recordText) {

        recordText.innerText =
            "Start Speaking";
    }


    if (status) {

        status.innerText = "Ready";

        status.classList.remove(
            "active"
        );
    }
}


function getSpeechRecognitionLanguage(language) {

    const languages = {

        "en": "en-IN",
        "hi": "hi-IN",
        "te": "te-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "bn": "bn-IN",
        "mr": "mr-IN",
        "gu": "gu-IN",
        "fr": "fr-FR",
        "de": "de-DE",
        "es": "es-ES",
        "it": "it-IT",
        "pt": "pt-PT",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "zh-CN": "zh-CN",
        "ar": "ar-SA",
        "ru": "ru-RU"
    };

    return languages[language] || "en-IN";
}


async function translateText() {

    if (isTranslating) {
        return;
    }


    const inputText =
        document.getElementById(
            "inputText"
        ).value.trim();


    const sourceLanguage =
        document.getElementById(
            "sourceLanguage"
        ).value;


    const targetLanguage =
        document.getElementById(
            "targetLanguage"
        ).value;


    if (!inputText) {

        alert(
            "Please speak something or enter text first."
        );

        return;
    }


    if (
        sourceLanguage === targetLanguage
    ) {

        document.getElementById(
            "outputText"
        ).value = inputText;

        document.getElementById(
            "speakButton"
        ).disabled = false;

        return;
    }


    isTranslating = true;


    const translateButton =
        document.getElementById(
            "translateButton"
        );


    if (translateButton) {

        translateButton.disabled = true;

        translateButton.innerText =
            "Translating...";
    }


    showProcessing(
        true,
        "Translating your speech..."
    );


    try {

        const response =
            await fetch(
                "/translate",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        text: inputText,

                        source_language:
                            sourceLanguage,

                        target_language:
                            targetLanguage
                    })
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(data.message);

            return;
        }


        document.getElementById(
            "outputText"
        ).value =
            data.translated_text;


        document.getElementById(
            "speakButton"
        ).disabled = false;


    } catch (error) {

        console.error(error);

        alert(
            "Something went wrong while translating."
        );

    } finally {

        isTranslating = false;

        if (translateButton) {

            translateButton.disabled = false;

            translateButton.innerText =
                "Translate";
        }

        showProcessing(false);
    }
}


async function speakTranslation() {

    const text =
        document.getElementById(
            "outputText"
        ).value.trim();


    const language =
        document.getElementById(
            "targetLanguage"
        ).value;


    if (!text) {

        alert(
            "There is no translated text."
        );

        return;
    }


    const speakButton =
        document.getElementById(
            "speakButton"
        );


    speakButton.disabled = true;

    speakButton.innerText =
        "Creating Audio...";


    try {

        const response =
            await fetch(
                "/speech",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        text: text,

                        language: language
                    })
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(data.message);

            speakButton.disabled = false;

            speakButton.innerText =
                "Play Translation";

            return;
        }


        const audio =
            new Audio(
                data.audio_url
            );


        audio.play();


        audio.onended =
            function () {

                speakButton.innerText =
                    "Play Translation";

                speakButton.disabled =
                    false;
            };


    } catch (error) {

        console.error(error);

        alert(
            "Unable to create speech."
        );

        speakButton.innerText =
            "Play Translation";

        speakButton.disabled =
            false;
    }
}


function clearInput() {

    document.getElementById(
        "inputText"
    ).value = "";

    document.getElementById(
        "outputText"
    ).value = "";

    document.getElementById(
        "speakButton"
    ).disabled = true;
}


function swapLanguages() {

    const source =
        document.getElementById(
            "sourceLanguage"
        );


    const target =
        document.getElementById(
            "targetLanguage"
        );


    if (source.value === "auto") {

        alert(
            "Please select a source language before swapping."
        );

        return;
    }


    const oldSource =
        source.value;


    source.value =
        target.value;


    target.value =
        oldSource;


    const input =
        document.getElementById(
            "inputText"
        );


    const output =
        document.getElementById(
            "outputText"
        );


    const oldText =
        input.value;


    input.value =
        output.value;


    output.value =
        oldText;


    document.getElementById(
        "speakButton"
    ).disabled =
        !output.value;
}


function showProcessing(show, text) {

    const area =
        document.getElementById(
            "processingArea"
        );


    const processingText =
        document.getElementById(
            "processingText"
        );


    if (!area) {
        return;
    }


    if (show) {

        area.classList.add("show");

        processingText.innerText =
            text || "Processing...";

    } else {

        area.classList.remove(
            "show"
        );
    }
}