# Tarefa

Você é um grande historiador de arte e um ótimo romancista.

Estamos construindo uma história baseada em diferentes obras de arte selecionadas por pacientes com demência. Escreva uma história que se inspire nessas cenas. Use por volta de 10 frases. Conte como uma história simples e fluida, com um início, meio e fim claros. Os parágrafos devem estar conectados e seguir uma sequência lógica de eventos. A história deve ser em português.

# Formato de Saída

Após escrever a história, você deve fornecer:

1. **text**: O texto completo da história
2. **Events**: Exatamente 4 eventos da história, cada um como uma frase curta (2-6 palavras), listados em ordem cronológica conforme ocorrem na história
4. **Environment**: O ambiente da história. Escolha um: Aberto, Urbano, Fechado ou Rural
5. **TimeOfDay**: A parte do dia na história. Escolha um: Manhã, Tarde ou Noite
6. **Emotion**: A emoção predominante na história. Escolha um: Felicidade, Tristeza, Raiva, Supresa ou Nojo


# Output
```json
{
  "text": "O texto completo da história aqui...",
  "events": [
    "Primeira frase de evento",
    "Segunda frase de evento",
    "Terceira frase de evento",
    "Quarta frase de evento"
  ],
  "environment": "Aberto",
  "timeOfDay": "Manhã",
  "emotion": "Felicidade"
}
```