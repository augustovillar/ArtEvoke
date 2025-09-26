# Internacionalização (i18n) - ArtEvoke Frontend

Esta pasta contém toda a configuração de internacionalização da aplicação.

## Estrutura

```
i18n/
├── index.js              # Configuração principal do i18next
├── detector.js           # Detector de idioma do browser
└── translations/         # Traduções organizadas por idioma
    ├── en/              # Inglês
    │   ├── common.json  # Traduções comuns
    │   └── index.js     # Export das traduções
    └── pt/              # Português
        ├── common.json  # Traduções comuns
        └── index.js     # Export das traduções
```

## Como usar

1. **Importar no App.js**: `import './i18n';`
2. **Usar nos componentes**: `const { t } = useTranslation();`
3. **Adicionar novas traduções**: Editar os arquivos `common.json`
4. **Adicionar novo idioma**: 
   - Criar pasta `translations/[idioma]/`
   - Adicionar `common.json` e `index.js`
   - Importar no `i18n/index.js`

## Idiomas suportados

- **en**: Inglês (padrão)
- **pt**: Português

## Detecção de idioma

O sistema detecta o idioma na seguinte ordem:
1. localStorage (preferência salva)
2. navigator (idioma do browser)
3. htmlTag (atributo lang do HTML)
