/**
 * Read an audio file's duration in the browser, without uploading it.
 * Returns null when the browser cannot tell (some WebM files report Infinity);
 * the server still enforces the real limit.
 */
export function getAudioDuration(file: File): Promise<number | null> {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const audio = new Audio();
    audio.preload = "metadata";

    const done = (value: number | null) => {
      URL.revokeObjectURL(url);
      resolve(value);
    };

    audio.onloadedmetadata = () =>
      done(Number.isFinite(audio.duration) ? audio.duration : null);
    audio.onerror = () => done(null);
    audio.src = url;
  });
}
