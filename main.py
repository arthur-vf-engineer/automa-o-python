import os
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---- Configuração ----------------------------------------------------------

_URL_LOGIN = "https://extranet.grupoboticario.com.br/"
_URL_LOGGED_HOME = "**/home"  # Coringa para validar que o login passou
_URL_TARGET = "https://extranet.grupoboticario.com.br/mfe/gi/direct-sales-view/base-monitoring"
_USER_ENV = "BOTI_USER"
_PASS_ENV = "BOTI_PASS"

# ---------------------------------------------------------------------------


def perform_login_and_navigate() -> None:
    usuario = os.environ.get(_USER_ENV, "arthur.farias")
    senha = os.environ.get(_PASS_ENV, "Moluscao63+")

    if not usuario or not senha:
        raise RuntimeError(
            f"Credenciais não encontradas nas variáveis de ambiente "
            f"{_USER_ENV} / {_PASS_ENV}"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ])

        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 800},
            accept_downloads=True
        )
        page = context.new_page()

        try:
            print("Acessando página de login...")
            page.goto(_URL_LOGIN, timeout=60_000)

            page.locator("#signInName").fill(usuario)
            page.locator("#password").fill(senha)
            page.locator("#next").click()

            print("Aguardando autenticação...")
            page.wait_for_url(_URL_LOGGED_HOME, timeout=60_000)
            print("Login concluído com sucesso!")

            print(f"Redirecionando para: {_URL_TARGET}")
            page.goto(_URL_TARGET, timeout=60_000)
            print("Página alvo carregada!")

            # =================================================================
            # ETAPAS DE EXTRAÇÃO
            # =================================================================
            print("\nIniciando extração em lote...")

            # 1. Cria a pasta para salvar os ciclos isolados caso não exista
            pasta_ciclos = "ciclos_anteriores"
            os.makedirs(pasta_ciclos, exist_ok=True)

            # 2. Fecha os modais iniciais exatamente como fornecido
            # page.get_by_role("button", name="Fechar").click()
            # page.get_by_role("button", name="Fechar").click()

            # Ajuste os ciclos conforme a necessidade
            ciclos_para_baixar = [1, 2, 3, 4, 5, 6]

            # 3. Loop para baixar ciclo por ciclo
            for ciclo in ciclos_para_baixar:
                print(f"\n--- Processando Ciclo {ciclo} ---")

                # Abre o dropdown de ciclos
                page.get_by_placeholder("Ciclo atual:").click()

                # Clica no ciclo desejado
                page.get_by_role("button", name=f"Ciclo {ciclo}").click()

                # Lida com o modal "Agora não" se ele aparecer
                botao_agora_nao = page.get_by_role("button", name="Agora não")
                if botao_agora_nao.is_visible():
                    botao_agora_nao.click()

                # Processo de Exportação
                page.get_by_test_id("button-export").click()
                page.get_by_label("Exportar Planilha").get_by_text(
                    "Penetração de base no período").click()

                print(f"Aguardando geração do arquivo do Ciclo {ciclo}...")
                with page.expect_download(timeout=120_000) as download_info:
                    page.get_by_test_id("btn-export-modal").click()

                download = download_info.value

                # Salva os arquivos dentro da pasta "ciclos_anteriores"
                nome_arquivo = os.path.join(
                    pasta_ciclos, f"base_monitoramento_ciclo_{ciclo}.xlsx")
                download.save_as(nome_arquivo)

                print(f"Salvo com sucesso: {nome_arquivo}")

                # Pausa para garantir que os modais sumam antes do próximo loop
                page.wait_for_timeout(2000)

            print("\nProcesso de download concluído com sucesso!")
            # =================================================================

        except PWTimeout as err:
            raise RuntimeError(f"Timeout durante a execução: {err}") from err
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
        finally:
            print("Encerrando o contexto e o navegador...")
            context.close()
            browser.close()


if __name__ == "__main__":
    perform_login_and_navigate()
