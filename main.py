import time
import schedule
from datetime import datetime, timedelta

from source.reports import ReportClient
from source.utils import salvar_relatorio_em_pasta
from source.transformacao import main

# -------------------------------------------------------------------
def run_report() -> None:
    """Baixa e salva relatórios dos últimos 31 dias (incluindo hoje)."""
    client = ReportClient()
    
    # Define end_date como hoje e start_date como 31 dias antes
    end_date = datetime.now()
    start_date = end_date - timedelta(days=31)
    
    print(f"[{datetime.now():%H:%M:%S}] Baixando relatórios de {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")

    # Loop para cada dia no intervalo
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"[{datetime.now():%H:%M:%S}] Gerando relatório de {date_str}")

        try:
            # Baixa relatório do dia atual
            bin_data = client.get_report(start_date=date_str, end_date=date_str)
            
            # Salva o relatório
            salvar_relatorio_em_pasta(
                bin_data,
                start_date=date_str,
                base_dir="relatorios",
                nome_arquivo=f"{date_str}.xlsx",
            )
            print(f"[OK] Relatório salvo em relatorios/{date_str}.xlsx")
        except Exception as e:
            print(f"[ERRO] Falha em {date_str}: {e}")

        # Avança para o próximo dia
        current_date += timedelta(days=1)

# -------------------------------------------------------------------

if __name__ == "__main__":
    run_report()
    print("Aguardando 15 segundos para garantir que os relatórios foram salvos...")
    time.sleep(15) 
    
    main()
    print("Aguardando 30 segundos para garantir que a base foi exportada...")
    time.sleep(15)

# ----------------------------------------------------------------------------------------------------------------------------------------- #

# import time
# from datetime import datetime, timedelta
# from source.reports import ReportClient
# from source.utils import salvar_relatorio_em_pasta
# from source.transformacao import main

# def run_report() -> None:
#     """Baixa e salva relatórios de todos os dias do ano atual (dia a dia)."""
#     client = ReportClient()
    
#     # Obtém o ano atual
#     ano_atual = datetime.now().year - 1
    
#     # Define start_date como 01/01 do ano atual
#     start_date = datetime(ano_atual, 1, 1)
    
#     # Define end_date como hoje (ou 31/12 se quiser todo o ano)
#     end_date = datetime.now()  # Para pegar até hoje
#     # end_date = datetime(ano_atual, 12, 31)  # Para pegar até 31/12 independente do dia atual
    
#     print(f"[{datetime.now():%H:%M:%S}] Baixando relatórios de {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")

#     # Loop para cada dia no intervalo
#     current_date = start_date
#     while current_date <= end_date:
#         date_str = current_date.strftime("%Y-%m-%d")
#         print(f"[{datetime.now():%H:%M:%S}] Gerando relatório de {date_str}")

#         try:
#             # Baixa relatório do dia atual
#             bin_data = client.get_report(start_date=date_str, end_date=date_str)
            
#             # Salva o relatório
#             salvar_relatorio_em_pasta(
#                 bin_data,
#                 start_date=date_str,
#                 base_dir="relatorios",
#                 nome_arquivo=f"{date_str}.xlsx",
#             )
#             print(f"[OK] Relatório salvo em relatorios/{date_str}.xlsx")
#         except Exception as e:
#             print(f"[ERRO] Falha em {date_str}: {e}")

#         # Avança para o próximo dia
#         current_date += timedelta(days=1)

# if __name__ == "__main__":
#     run_report()
#     print("Aguardando 15 segundos para garantir que os relatórios foram salvos...")
#     time.sleep(15) 
    
#     main()
#     print("Aguardando 30 segundos para garantir que a base foi exportada...")
#     time.sleep(15)