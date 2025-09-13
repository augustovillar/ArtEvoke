export function speakWithPauses(textBlocks, pauseMs = 500) {
  if (!window.speechSynthesis) return;

  let i = 0;

  function speakNext() {
    if (i >= textBlocks.length) return;
    const utterance = new SpeechSynthesisUtterance(textBlocks[i]);
    utterance.onend = () => {
      setTimeout(() => {
        i++;
        speakNext();
      }, pauseMs);
    };
    window.speechSynthesis.speak(utterance);
  }

  window.speechSynthesis.cancel();
  speakNext();
}