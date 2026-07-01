// This runs in a separate browser thread (AudioWorkletGlobalScope).
// It receives raw PCM samples from the microphone and posts them
// back to the main thread as 16-bit integer arrays.
class AudioProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        if (input.length > 0) {
            const float32 = input[0]; // mono channel, float32 samples

            // Convert float32 [-1, 1] to int16 [-32768, 32767]
            // This is linear16 / PCM16 format — what Deepgram expects
            const int16 = new Int16Array(float32.length);
            for (let i = 0; i < float32.length; i++) {
                const clamped = Math.max(-1, Math.min(1, float32[i]));
                int16[i] = clamped < 0 ? clamped * 32768 : clamped * 32767;
            }

            // Post the raw PCM chunk back to the main thread
            this.port.postMessage(int16.buffer, [int16.buffer]);
        }
        return true; // keep processor alive
    }
}

registerProcessor("audio-processor", AudioProcessor);