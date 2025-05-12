-- 💡 Здесь перечислены модели, доступные в системе.
-- Вы можете изменить или дополнить список в соответствии с теми LLM, которые установлены у вас.
--
-- 📌 Важно:
-- - 'name' — техническое имя модели (используется в запросах)
-- - 'provider' — источник модели (например, openai, ollama, openrouter и т.д.)
-- - 'is_public' — будет ли отображаться пользователю в списке
-- - 'display_name' — читаемое название модели для отображения во фронт
-- - 'plus_only' — если TRUE, то модель доступна только пользователям с подпиской Plus


INSERT INTO models (name, provider, is_public, display_name, plus_only) VALUES
  ('gemma:2b', 'ollama', true, 'Gemma 2B', false),
  ('phi', 'ollama', true, 'Phi-2', false),
  ('mistral', 'ollama', true, 'Mistral', true);