# Tarefa

Você é um grande historiador de arte e um ótimo romancista.

Estamos construindo uma história baseada em diferentes obras de arte selecionadas por pacientes com demência. Escreva uma história que se inspire nessas cenas. Use 2 parágrafos curtos. Conte como uma história simples e fluida, com um início, meio e fim claros. Os parágrafos devem estar conectados e seguir uma sequência lógica de eventos. A história deve ser em português.

# Formato de Saída

Após escrever a história, você deve fornecer:

1. **História**: O texto completo da história
2. **Eventos**: Exatamente 4 eventos da história, cada um como uma frase curta (2-6 palavras), listados em ordem cronológica conforme ocorrem na história
3. **Distrator**: Uma frase curta (2-6 palavras) que descreve algo que NÃO é um evento da história
4. **Ambiente**: O ambiente da história. Escolha um: Aberto, Urbano, Fechado ou Rural
5. **ParteDoDia**: A parte do dia na história. Escolha um: Manhã, Tarde ou Noite
6. **Emoção**: A emoção predominante na história. Escolha um: Felicidade, Tristeza, Raiva, Surpresa ou Nojo

Formate sua resposta como JSON com a seguinte estrutura:
```json
{
  "story": "O texto completo da história aqui...",
  "events": [
    "Primeira frase de evento",
    "Segunda frase de evento",
    "Terceira frase de evento",
    "Quarta frase de evento"
  ],
  "distractor": "Uma frase que não é um evento da história",
  "environment": "Aberto",
  "timeOfDay": "Manhã",
  "emotion": "Felicidade"
}
```
