from pydantic import BaseModel, ConfigDict, Field

from tp_shared.ocr_service.types.ocr_doc_type import DocType


class STSFields(BaseModel):
    vin: str | None = Field(None, description="🚗 VIN номер автомобиля")
    reg_number: str | None = Field(None, description="🔢 Регистрационный номер")
    sts_number: str | None = Field(None, description="📋 Номер СТС")
    owner_name: str | None = Field(None, description="👤 ФИО владельца")
    model: str | None = Field(None, description="🚙 Модель автомобиля")
    reg_date: str | None = Field(None, description="📅 Дата регистрации")

    model_config = ConfigDict(populate_by_name=True)


class DriverLicenseFrontFields(BaseModel):
    license_number: str | None = Field(
        None, description="🪪 Номер водительского удостоверения"
    )
    owner_name: str | None = Field(None, description="👤 ФИО владельца")
    birth_date: str | None = Field(None, description="🎂 Дата рождения")
    issue_date: str | None = Field(None, description="📅 Дата выдачи")
    expiry_date: str | None = Field(None, description="⏰ Дата окончания действия")
    issuer: str | None = Field(None, description="🏢 Орган, выдавший удостоверение")

    model_config = ConfigDict(populate_by_name=True)


class DriverLicenseBackFields(BaseModel):
    categories: str | None = Field(None, description="🚙 Категории вождения")

    model_config = ConfigDict(populate_by_name=True)


class PassportFields(BaseModel):
    passport_number: str | None = Field(None, description="📄 Серия и номер паспорта")
    surname: str | None = Field(None, description="👨 Фамилия")
    name: str | None = Field(None, description="👤 Имя")
    patronymic: str | None = Field(None, description="👨👦 Отчество")
    birth_date: str | None = Field(None, description="🎂 Дата рождения")
    birth_place: str | None = Field(None, description="🌍 Место рождения")
    issue_date: str | None = Field(None, description="📅 Дата выдачи")
    issued_by: str | None = Field(None, description="🏢 Кем выдан")
    division_code: str | None = Field(None, description="🔢 Код подразделения")

    model_config = ConfigDict(populate_by_name=True)


class OrgCardFields(BaseModel):
    org_name: str | None = Field(None, description="🏢 Название организации")
    inn: str | None = Field(None, description="🔢 ИНН")
    kpp: str | None = Field(None, description="📊 КПП")
    address: str | None = Field(None, description="📍 Адрес")
    phone: str | None = Field(None, description="📞 Телефон")
    email: str | None = Field(None, description="📧 Email")
    manager: str | None = Field(None, description="👨💼 Руководитель")

    model_config = ConfigDict(populate_by_name=True)


DocumentFields = (
    STSFields
    | DriverLicenseFrontFields
    | DriverLicenseBackFields
    | PassportFields
    | OrgCardFields
)


class OCRResponse(BaseModel):
    doc_type: DocType = Field(None, description="📄 Тип обработанного документа")
    fields: DocumentFields = Field(None, description="📊 Извлеченные поля документа")
