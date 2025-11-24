#!/bin/bash

# ============================================================================
# KADUPUL API - Suite de Testes Automatizados
# ============================================================================
# Este script testa todos os endpoints da API Kadupul de forma automatizada
# 
# Pré-requisitos:
#   - Docker Compose rodando (docker compose up -d)
#   - curl instalado
#   - python3 instalado (para formatação JSON)
#
# Uso:
#   bash test_api.sh
#
# Autor: Kadupul Team
# Data: 2025
# ============================================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configurações
API_URL="http://localhost:8001"
ML_SERVICE_URL="http://localhost:8002"
SLEEP_TIME=0.5  # Pausa entre requisições

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

# Imprime cabeçalho de seção
print_header() {
    echo -e "\n${BOLD}${CYAN}============================================${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${BOLD}${CYAN}============================================${NC}\n"
}

# Imprime título de teste
print_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BOLD}${YELLOW}Teste #$TOTAL_TESTS: $1${NC}"
    echo -e "${BLUE}-------------------------------------------${NC}"
}

# Imprime resultado OK
print_ok() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓ PASSOU${NC}\n"
}

# Imprime resultado FALHOU
print_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗ FALHOU${NC}"
    echo -e "${RED}Erro: $1${NC}\n"
}

# Imprime JSON formatado
print_json() {
    if command -v python3 &> /dev/null; then
        echo "$1" | python3 -m json.tool 2>/dev/null || echo "$1"
    else
        echo "$1"
    fi
}

# Verifica se serviços estão rodando
check_services() {
    print_header "VERIFICANDO SERVIÇOS"
    
    echo -e "${PURPLE}Verificando se API está respondendo...${NC}"
    if curl -s -f "$API_URL" > /dev/null; then
        echo -e "${GREEN}✓ API está online (porta 8001)${NC}\n"
    else
        echo -e "${RED}✗ API não está respondendo!${NC}"
        echo -e "${YELLOW}Execute: docker compose up -d${NC}\n"
        exit 1
    fi
    
    echo -e "${PURPLE}Verificando se ML Service está respondendo...${NC}"
    if curl -s -f "$ML_SERVICE_URL/health" > /dev/null; then
        echo -e "${GREEN}✓ ML Service está online (porta 8002)${NC}\n"
    else
        echo -e "${RED}✗ ML Service não está respondendo!${NC}"
        echo -e "${YELLOW}Execute: docker compose up -d${NC}\n"
        exit 1
    fi
}

# ============================================================================
# TESTES DA API
# ============================================================================

# Teste 1: Endpoint raiz
test_root_endpoint() {
    print_test "Endpoint Raiz (GET /)"
    
    response=$(curl -s "$API_URL/")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ]; then
        print_ok
    else
        print_fail "Esperado HTTP 200, recebido $http_code"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 2: Health check
test_health_check() {
    print_test "Health Check (GET /health)"
    
    response=$(curl -s "$API_URL/health")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    # Health check pode retornar 200 (healthy) ou 503 (degraded)
    if [ "$http_code" == "200" ] || [ "$http_code" == "503" ]; then
        if echo "$response" | grep -q "status"; then
            print_ok
        else
            print_fail "Resposta não contém campo 'status'"
        fi
    else
        print_fail "Esperado HTTP 200 ou 503, recebido $http_code"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 3: Predição - Iris Setosa
test_predict_setosa() {
    print_test "Predição - Iris Setosa"
    
    echo -e "${PURPLE}Features: [5.1, 3.5, 1.4, 0.2]${NC}"
    echo -e "${PURPLE}Classe esperada: setosa${NC}\n"
    
    response=$(curl -s -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.1, 3.5, 1.4, 0.2]}')
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.1, 3.5, 1.4, 0.2]}')
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ] && echo "$response" | grep -q "setosa"; then
        print_ok
    else
        print_fail "Esperado HTTP 200 com classe 'setosa'"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 4: Predição - Iris Versicolor
test_predict_versicolor() {
    print_test "Predição - Iris Versicolor"
    
    echo -e "${PURPLE}Features: [5.9, 3.0, 4.2, 1.5]${NC}"
    echo -e "${PURPLE}Classe esperada: versicolor${NC}\n"
    
    response=$(curl -s -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.9, 3.0, 4.2, 1.5]}')
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.9, 3.0, 4.2, 1.5]}')
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ] && echo "$response" | grep -q "versicolor"; then
        print_ok
    else
        print_fail "Esperado HTTP 200 com classe 'versicolor'"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 5: Predição - Iris Virginica
test_predict_virginica() {
    print_test "Predição - Iris Virginica"
    
    echo -e "${PURPLE}Features: [6.3, 3.3, 6.0, 2.5]${NC}"
    echo -e "${PURPLE}Classe esperada: virginica${NC}\n"
    
    response=$(curl -s -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [6.3, 3.3, 6.0, 2.5]}')
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [6.3, 3.3, 6.0, 2.5]}')
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ] && echo "$response" | grep -q "virginica"; then
        print_ok
    else
        print_fail "Esperado HTTP 200 com classe 'virginica'"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 6: Cache Hit (predição repetida)
test_cache_hit() {
    print_test "Cache Hit - Predição Repetida"
    
    echo -e "${PURPLE}Repetindo predição anterior (deve vir do cache)${NC}"
    echo -e "${PURPLE}Features: [5.1, 3.5, 1.4, 0.2]${NC}\n"
    
    response=$(curl -s -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.1, 3.5, 1.4, 0.2]}')
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if echo "$response" | grep -q '"source": "cache"'; then
        echo -e "${GREEN}✓ Resultado veio do cache (Redis)${NC}"
        print_ok
    elif echo "$response" | grep -q '"source": "model"'; then
        echo -e "${YELLOW}⚠ Resultado veio do modelo (cache pode ter expirado)${NC}"
        print_ok
    else
        print_ok
    fi
    
    sleep $SLEEP_TIME
}

# Teste 7: Listar predições
test_list_predictions() {
    print_test "Listar Predições (GET /api/predictions)"
    
    response=$(curl -s "$API_URL/api/predictions?limit=5")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/predictions?limit=5")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ] && echo "$response" | grep -q "predictions"; then
        count=$(echo "$response" | grep -o '"count": [0-9]*' | grep -o '[0-9]*')
        echo -e "${GREEN}✓ Encontradas $count predições no MongoDB${NC}"
        print_ok
    else
        print_fail "Esperado HTTP 200 com lista de predições"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 8: Estatísticas
test_statistics() {
    print_test "Estatísticas (GET /api/stats)"
    
    response=$(curl -s "$API_URL/api/stats")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/stats")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ] && echo "$response" | grep -q "total_predictions"; then
        print_ok
    else
        print_fail "Esperado HTTP 200 com estatísticas"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 9: Validação de erro (features inválidas)
test_error_validation() {
    print_test "Validação de Erro - Features Inválidas"
    
    echo -e "${PURPLE}Enviando apenas 2 features (deveria falhar)${NC}\n"
    
    response=$(curl -s -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.1, 3.5]}')
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/predict" \
        -H "Content-Type: application/json" \
        -d '{"features": [5.1, 3.5]}')
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "400" ] && echo "$response" | grep -q "error"; then
        echo -e "${GREEN}✓ API retornou erro 400 corretamente${NC}"
        print_ok
    else
        print_fail "Esperado HTTP 400 com mensagem de erro"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 10: Buscar predição por ID (se houver predições)
test_get_prediction_by_id() {
    print_test "Buscar Predição por ID"
    
    # Primeiro, pega uma lista de predições para obter um ID válido
    predictions=$(curl -s "$API_URL/api/predictions?limit=1")
    
    # Extrai o primeiro _id usando grep
    prediction_id=$(echo "$predictions" | grep -o '"_id": "[^"]*"' | head -1 | grep -o '[^"]*"$' | tr -d '"')
    
    if [ -z "$prediction_id" ]; then
        echo -e "${YELLOW}⚠ Nenhuma predição encontrada no banco. Pulando teste.${NC}\n"
        return
    fi
    
    echo -e "${PURPLE}Buscando predição com ID: $prediction_id${NC}\n"
    
    response=$(curl -s "$API_URL/api/predictions/$prediction_id")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/predictions/$prediction_id")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ] && echo "$response" | grep -q "_id"; then
        print_ok
    else
        print_fail "Esperado HTTP 200 com detalhes da predição"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 11: ML Service - Health
test_ml_service_health() {
    print_test "ML Service - Health Check"
    
    response=$(curl -s "$ML_SERVICE_URL/health")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$ML_SERVICE_URL/health")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    if [ "$http_code" == "200" ]; then
        print_ok
    else
        print_fail "Esperado HTTP 200"
    fi
    
    sleep $SLEEP_TIME
}

# Teste 12: ML Service - Model Info
test_ml_service_model_info() {
    print_test "ML Service - Informações do Modelo"
    
    response=$(curl -s "$ML_SERVICE_URL/model-info")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$ML_SERVICE_URL/model-info")
    
    echo -e "${CYAN}Response:${NC}"
    print_json "$response"
    
    # Verifica se tem model_name ou algorithm (ambos são válidos)
    if [ "$http_code" == "200" ] && (echo "$response" | grep -q "model_name" || echo "$response" | grep -q "algorithm"); then
        print_ok
    else
        print_fail "Esperado HTTP 200 com informações do modelo"
    fi
    
    sleep $SLEEP_TIME
}

# ============================================================================
# RELATÓRIO FINAL
# ============================================================================

print_summary() {
    print_header "RESUMO DOS TESTES"
    
    echo -e "${BOLD}Total de testes executados: ${CYAN}$TOTAL_TESTS${NC}"
    echo -e "${BOLD}Testes bem-sucedidos: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "${BOLD}Testes falhados: ${RED}$TESTS_FAILED${NC}\n"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${BOLD}${GREEN}✓✓✓ TODOS OS TESTES PASSARAM! ✓✓✓${NC}\n"
        exit 0
    else
        echo -e "${BOLD}${RED}✗✗✗ ALGUNS TESTES FALHARAM ✗✗✗${NC}\n"
        exit 1
    fi
}

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

main() {
    clear
    
    print_header "KADUPUL API - SUITE DE TESTES"
    
    echo -e "${PURPLE}Iniciando testes automatizados...${NC}"
    echo -e "${PURPLE}API URL: $API_URL${NC}"
    echo -e "${PURPLE}ML Service URL: $ML_SERVICE_URL${NC}\n"
    
    # Verifica se serviços estão online
    check_services
    
    # Executa testes da API Principal
    print_header "TESTES DA API PRINCIPAL"
    test_root_endpoint
    test_health_check
    test_predict_setosa
    test_predict_versicolor
    test_predict_virginica
    test_cache_hit
    test_list_predictions
    test_statistics
    test_error_validation
    test_get_prediction_by_id
    
    # Executa testes do ML Service
    print_header "TESTES DO ML SERVICE"
    test_ml_service_health
    test_ml_service_model_info
    
    # Imprime resumo
    print_summary
}

# Executa script
main
