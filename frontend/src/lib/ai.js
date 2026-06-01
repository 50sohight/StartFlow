const AI_BASE = 'http://localhost:8001';

export async function generateProjectReport(documents) {
  const res = await fetch(`${AI_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_query:
        'На основе этих данных составь аналитический отчёт о состоянии проекта. Опиши прогресс, возможные узкие места, дай рекомендации.',
      documents,
      response_type: 'text',
      temperature: 0.3,
      top_k: 50,
      max_tokens: 512
    })
  });
  if (!res.ok) throw new Error('Ошибка AI');
  const data = await res.json();
  return data.text_response || data.raw_answer || 'Нет ответа';
}