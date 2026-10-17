# Base inicial de prospecção da Spiralis

## O que foi verificado

- Fonte: contratos publicados na [API oficial do PNCP](https://pncp.gov.br/api/consulta/swagger-ui/index.html), de 1 a 15 de outubro de 2026.
- Amostra: seis páginas de 50 registros, distribuídas no resultado nacional. A API limitou chamadas posteriores com HTTP 429. O arquivo `amostra.json` registra as páginas efetivamente consultadas.
- A lista contém somente pessoas jurídicas identificadas por CNPJ. Um contrato recente indica experiência em fornecer ao setor público; não prova que a empresa procura software nem que responderá ao contato.
- Contatos foram incluídos só quando publicados em página empresarial ou documento público associado ao mesmo CNPJ. Telefone público **não** foi verificado como WhatsApp. Nenhuma mensagem foi enviada.

## Prioridade de abordagem

`prioridade_pontos` é uma **heurística de triagem**, não uma probabilidade estatística de resposta:

- 2 pontos: fornecedor PJ com contrato recente no PNCP;
- até 3 pontos: aparições adicionais na amostra coletada;
- até 2 pontos: valor do último contrato entre R$ 10 mil e R$ 500 mil (1 ponto em faixa ampliada);
- 1 ponto: publicação em 10 de outubro de 2026 ou depois.

O valor do contrato é um sinal fraco e deve ser revisado manualmente. A amostragem pode subcontar contratos de uma empresa. Há limite de quatro empresas por UF do órgão contratante na seleção final, para ampliar a cobertura geográfica. A UF é do **órgão comprador**, não necessariamente da sede do fornecedor.

## Fluxo sugerido

1. Validar empresa, site e atuação atual antes do contato.
2. Encontrar canal empresarial público e confirmar se o número aceita WhatsApp; não presumir isso a partir do telefone cadastral.
3. Personalizar a primeira linha com um fato verificável sobre a atuação em licitações, sem citar números de contrato se isso soar invasivo.
4. Registrar resposta, desinteresse e pedido de não contato. Não importar a lista diretamente para envio em massa.

## Abertura de WhatsApp para revisão humana

> Oi, tudo bem? Sou o Eduardo, CEO da Spiralis, uma startup de tecnologia. Estamos convidando algumas empresas que trabalham com licitações para testar por 14 dias uma ferramenta que acompanha oportunidades no PNCP, ajuda a conferir editais e avisa sobre prazos. Queremos acompanhar o uso de perto e melhorar com o retorno de quem vive essa rotina. Você é a pessoa que cuida das licitações por aí?

O Harvey original é focado em e-mail e descoberta de negócios locais. O arquivo `harvey.yaml` foi ajustado para a Spiralis, com canais de envio desativados. O script desta pasta faz a descoberta inicial a partir do PNCP. A etapa de WhatsApp permanece manual.

## Atualizar a base

Execute `python prospecting/build_pncp_leads.py` na raiz do repositório. O script preserva contatos já verificados de empresas que continuem na seleção. Antes de uma coleta futura, atualize o período no script. Respeite as respostas de limitação de taxa da API.
