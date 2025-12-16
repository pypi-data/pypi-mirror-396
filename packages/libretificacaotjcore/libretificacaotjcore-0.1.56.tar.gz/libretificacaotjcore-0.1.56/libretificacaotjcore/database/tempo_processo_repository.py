from datetime import datetime
import uuid
from pymongo.errors import BulkWriteError

from libretificacaotjcore.dtos.processo_dto import ProcessoDto
from libretificacaotjcore.enums.e_fase_retificacao import EFaseRetificacao

class TempoProcessoRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_processo(self, *, processo: ProcessoDto) -> bool:
        try:
            processo_dict = processo.model_dump(exclude_none=True)
            processo_dict["DataInicio"] = processo.DataInicio.strftime("%Y-%m-%d")
            processo_dict["DataFim"] = processo.DataFim.strftime("%Y-%m-%d")
            processo_dict["FaseDescricao"] = EFaseRetificacao(processo.Fase).name

            processo_no_db = await self.__db.tempo_processos.find_one(
                {
                    "SolicitacaoId": processo.SolicitacaoId,
                    "Fase": processo.Fase,
                    "DataInicio": processo_dict["DataInicio"],
                    "DataFim": processo_dict["DataFim"],
                }
            )
            
            processo_dict["id"] = str(uuid.uuid4())

            if processo_no_db is None:
                processo_dict["InicioProcesso"] = datetime.now()
                await self.__db.tempo_processos.insert_one(processo_dict)
                return True

            await self.__db.tempo_processos.delete_one(
                {
                    "SolicitacaoId": processo.SolicitacaoId,
                    "Fase": processo.Fase,
                    "DataInicio": processo_dict["DataInicio"],
                    "DataFim": processo_dict["DataFim"],
                }
            )

            processo_dict["InicioProcesso"] = datetime.now()
            await self.__db.tempo_processos.insert_one(processo_dict)
            return True
        
        except Exception as e:
            print(f"❌ Erro ao inserir o processo: {e}")
            return False
        
    async def atualizar_processo(self, *, processo: ProcessoDto) -> bool:
        try:
            processo_dict = processo.model_dump()
            processo_dict["DataInicio"] = processo.DataInicio.strftime("%Y-%m-%d")
            processo_dict["DataFim"] = processo.DataFim.strftime("%Y-%m-%d")
             
            processo_no_db = await self.__db.tempo_processos.find_one(
                {
                    "SolicitacaoId": processo.SolicitacaoId,
                    "Fase": processo.Fase,
                    "DataInicio": processo_dict["DataInicio"],
                    "DataFim": processo_dict["DataFim"],
                }
            )

            if processo_no_db is None:
                return False
            
            processo_no_db['FimProcesso'] = datetime.now()
            tempo_de_processo = self._tempo_de_processo(processo_no_db['InicioProcesso'], processo_no_db['FimProcesso'])
            processo_no_db['TempoDeProcesso'] = tempo_de_processo

            await self.__db.tempo_processos.update_one(
                {
                    "SolicitacaoId": processo.SolicitacaoId,
                    "Fase": processo.Fase,
                    "DataInicio": processo_dict["DataInicio"],
                    "DataFim": processo_dict["DataFim"],
                },
                {"$set": processo_no_db
            })
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar o processo: {e}")
            return False

    async def buscar_por_solicitacao_id(self, solicitacao_id: int) -> list[ProcessoDto]:
        try:
            processos = await self.__db.tempo_processos.find(
                {
                    "SolicitacaoId": solicitacao_id
                }
            ).to_list(length=None)
            processos_dto = []

            for processo in processos:
                processo_dto = ProcessoDto(**processo)
                processos_dto.append(processo_dto)

            return processos_dto
        except Exception as e:
            print(f"❌ Erro ao buscar os processos por solicitação: {e}")
            return []
        
    def _tempo_de_processo(self, tempo_inicio: datetime, tempo_fim: datetime) -> str | None:
        if tempo_inicio and tempo_fim:
            delta = tempo_fim - tempo_inicio
            total_segundos = int(delta.total_seconds())

            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            segundos = total_segundos % 60

            tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            tempo_formatado = "00:00:01" if tempo_formatado == "00:00:00" else tempo_formatado
            return tempo_formatado

        return None
