const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Check backend connectivity and speech services health status.
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
    });
    if (!response.ok) {
      return { status: 'offline', configured: false };
    }
    return await response.json();
  } catch (error) {
    console.warn('Backend health check connection failed:', error);
    return { status: 'offline', configured: false, error: error.message };
  }
}

/**
 * Main Voice Pipeline: Sends recorded student audio Blob to FastAPI /api/ask.
 * Multipart field names match backend expectations: audio, language.
 */
export async function askQuestion(audioBlob, language = 'en') {
  if (!audioBlob || audioBlob.size === 0) {
    throw new Error('Recorded audio is empty. Please speak your question.');
  }

  const formData = new FormData();
  // Preserve actual recorded format extension (WebM, WAV, MP4) so backend PyAV can decode accurately
  const mimeType = audioBlob.type || 'audio/webm';
  let filename = 'recording.webm';
  if (mimeType.includes('wav')) filename = 'recording.wav';
  else if (mimeType.includes('mp4') || mimeType.includes('m4a')) filename = 'recording.mp4';
  else if (mimeType.includes('ogg')) filename = 'recording.ogg';

  formData.append('audio', audioBlob, filename);
  formData.append('language', language);

  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: 'POST',
    body: formData,
    // Note: Do not set Content-Type header; browser must auto-generate multipart boundary
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${response.status})`);
  }

  return await response.json();
}

/**
 * Text Query Pipeline for suggested campus questions.
 */
export async function queryText(query, language = 'en') {
  if (!query || !query.trim()) {
    throw new Error('Query text cannot be empty.');
  }

  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query: query.trim(), language }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${response.status})`);
  }

  return await response.json();
}

/**
 * Synthesize speech from text using Gnani Timbre TTS.
 */
export async function speakText(text, language = 'en', voice = null) {
  const payload = { text, language };
  if (voice) payload.voice = voice;

  const response = await fetch(`${API_BASE_URL}/api/speak`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Speech synthesis failed (${response.status})`);
  }

  const audioBlob = await response.blob();
  return URL.createObjectURL(audioBlob);
}
