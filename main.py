import time
import pandas as pd
from datetime import datetime, timedelta

from source.reports import ReportClient
from source.utils import salvar_relatorio_em_pasta
from source.transformacao import main as main_transformacao

# -------------------------------------------------------------------
def ler_pdvs_do_excel(caminho_arquivo="lojas.xlsx") -> list:
    """Lê a coluna B (segunda coluna) do arquivo Excel e retorna uma lista de PDVs."""
    try:
        df_lojas = pd.read_excel(caminho_arquivo)
        pdvs = df_lojas.iloc[:, 1].dropna().astype(str).str.replace(r'\.0$', '', regex=True).tolist()
        return pdvs
    except Exception as e:
        print(f"[ERRO] Falha ao ler o arquivo {caminho_arquivo}: {e}")
        return []

def run_report() -> None:
    pdvs = ler_pdvs_do_excel("lojas.xlsx")
    if not pdvs:
        print("Nenhum PDV encontrado no arquivo ou erro na leitura. Encerrando.")
        return

    client = ReportClient()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=11)
    
    print(f"[{datetime.now():%H:%M:%S}] Período definido: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
    print(f"Foram encontrados {len(pdvs)} PDVs para processar.\n")

    for pdv in pdvs:
        print(f"[{datetime.now():%H:%M:%S}] === INICIANDO DOWNLOAD PARA O PDV: {pdv} ===")
        
        current_date = start_date
        while current_date <= end_date:
            api_date_str = current_date.strftime("%Y-%m-%d")
            file_date_str = current_date.strftime("%d-%m-%Y")
            
            nome_arquivo_final = f"{file_date_str}-{pdv}.xlsx"

            print(f"  -> Baixando {api_date_str} (PDV {pdv})...", end=" ")

            try:
                bin_data = client.get_report(start_date=api_date_str, end_date=api_date_str, pdv=pdv)
                
                salvar_relatorio_em_pasta(
                    bin_data,
                    start_date=api_date_str, 
                    base_dir="relatorios",
                    nome_arquivo=nome_arquivo_final,
                )
                print(f"[OK] {nome_arquivo_final}")
            except Exception as e:
                print(f"[ERRO] {e}")

            current_date += timedelta(days=1)
            
        print(f"[{datetime.now():%H:%M:%S}] === PDV {pdv} FINALIZADO ===\n")

# -------------------------------------------------------------------

if __name__ == "__main__":
    run_report()
    print("Aguardando 15 segundos para garantir que todos os relatórios foram salvos...")
    time.sleep(15) 
    
    main_transformacao()
    print("Aguardando 30 segundos para garantir que a base foi exportada...")
    time.sleep(30)