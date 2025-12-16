from datetime import date, datetime, timedelta
from pydantic import BaseModel, ConfigDict, Field, field_validator
from libretificacaotjcore.enums.e_fase_retificacao import EFaseRetificacao


class ProcessoDto(BaseModel):
    model_config = ConfigDict(frozen=False)
    SolicitacaoId: int = Field(..., description="ID da solicitação")
    DataInicio: date = Field(..., description="Data de início no formato YYYY-MM-DD")
    DataFim: date = Field(..., description="Data de fim no formato YYYY-MM-DD")
    Fase: int | None = Field(None, description="Fase de retificação")
    InicioProcesso: datetime | None = Field(None, description="Data e hora de início do processo")
    FimProcesso: datetime | None = Field(None, description="Data e hora de fim do processo")
    TempoDeProcesso: str | None = Field(None, description="Tempo de processamento")
    Observacoes: str | None = Field(None, description="Observações adicionais")

    # --- Validadores ---

    @field_validator("SolicitacaoId")
    @classmethod
    def validar_solicitacao_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("O solicitacaoId deve ser um inteiro positivo.")
        return v

    @field_validator("DataInicio", mode="before")
    @classmethod
    def formatar_data_inicio(cls, value) -> date:
        """
        Aceita date, datetime ou string.
        """
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError as ve:
                raise ValueError("A DataInicio deve estar no formato YYYY-MM-DD.") from ve
        raise TypeError("Tipo inválido para DataInicio.")

    @field_validator("DataFim", mode="before")
    @classmethod
    def ajustar_data_fim(cls, value) -> date:
        """
        Aceita date, datetime ou string.
        Retorna o último dia do mês da data fornecida.
        """
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            ano, mes = value.year, value.month
        elif isinstance(value, str):
            try:
                ano, mes = map(int, value.split("-")[:2])
            except Exception:
                raise ValueError("A DataFim deve estar no formato YYYY-MM-DD.")
        else:
            raise TypeError("Tipo inválido para DataFim.")

        if mes < 1 or mes > 12:
            raise ValueError("A DataFim deve conter um mês válido (1–12).")

        # calcula o último dia do mês
        if mes == 12:
            proximo_mes = datetime(ano + 1, 1, 1)
        else:
            proximo_mes = datetime(ano, mes + 1, 1)
        return (proximo_mes - timedelta(days=1)).date()

    @field_validator("Fase")
    @classmethod
    def validar_fase(cls, v):
        if v is None:
            return v
        if v not in EFaseRetificacao:
            raise ValueError(f"Fase '{v}' não é válida.")
        return v
