let currentIA = "Version 1.0";

function selectPNJ(name) {
    currentIA = name;
    document.getElementById('pnj-title').innerText = name;
}

function send() {
    console.log("Tentative d'envoi..."); // On vérifie si la fonction se lance
    let msgInput = document.getElementById("msg");
    let msg = msgInput.value;
    if (!msg) return;

    let chatWindow = document.getElementById("chat-window");

    // Ajouter bulle utilisateur
    chatWindow.innerHTML += `<div class="message user-msg">${msg}</div>`;
    msgInput.value = "";
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Indicateur de réflexion
    let typingId = "typing-" + Date.now();
    chatWindow.innerHTML += `<div class="message ia-msg" id="${typingId}"><i>Réflexion en cours...</i></div>`;

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg, pnj: currentIA})
    })
    .then(r => r.json())
    .then(d => {
        let typingElem = document.getElementById(typingId);
        if (typingElem) {
            typingElem.innerHTML = d.reponse;
            chatWindow.scrollTop = chatWindow.scrollHeight;
            
            // Faire parler l'IA
            let utterance = new SpeechSynthesisUtterance(d.reponse);
            utterance.lang = 'fr-FR';
            window.speechSynthesis.speak(utterance);
        }
    })
    .catch(err => console.error("Erreur :", err));
}

// Permet d'envoyer avec la touche Entrée
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("msg").addEventListener("keypress", (e) => {
        if (e.key === "Enter") send();
    });
});