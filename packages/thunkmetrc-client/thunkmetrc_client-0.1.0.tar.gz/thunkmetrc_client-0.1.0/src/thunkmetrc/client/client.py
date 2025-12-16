import httpx
import base64
from typing import Any, Optional, Dict, List
from typing_extensions import TypedDict 
from typing import TypedDict

# --- Models ---

class Lab_testsCreaterecordV1RequestItem_Results(TypedDict, total=False):
    LabTestTypeName: str
    Notes: str
    Passed: bool
    Quantity: float

class Lab_testsCreaterecordV1RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    Label: str
    ResultDate: str
    Results: List[Lab_testsCreaterecordV1RequestItem_Results]

class Lab_testsCreaterecordV2RequestItem_Results(TypedDict, total=False):
    LabTestTypeName: str
    Notes: str
    Passed: bool
    Quantity: float

class Lab_testsCreaterecordV2RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    Label: str
    ResultDate: str
    Results: List[Lab_testsCreaterecordV2RequestItem_Results]

class Lab_testsUpdatelabtestdocumentV1RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    LabTestResultId: int

class Lab_testsUpdatelabtestdocumentV2RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    LabTestResultId: int

class Lab_testsUpdateresultreleaseV1RequestItem(TypedDict, total=False):
    PackageLabel: str

class Lab_testsUpdateresultreleaseV2RequestItem(TypedDict, total=False):
    PackageLabel: str

class LocationsCreateV1RequestItem(TypedDict, total=False):
    LocationTypeName: str
    Name: str

class LocationsCreateV2RequestItem(TypedDict, total=False):
    LocationTypeName: str
    Name: str

class LocationsCreateupdateV1RequestItem(TypedDict, total=False):
    Id: int
    LocationTypeName: str
    Name: str

class LocationsUpdateV2RequestItem(TypedDict, total=False):
    Id: int
    LocationTypeName: str
    Name: str

class PackagesCreateV1RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreateV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreateV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: bool
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateV2RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreateV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: bool
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateadjustV1RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    Label: str
    Quantity: int
    ReasonNote: str
    UnitOfMeasure: str

class PackagesCreateadjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    Label: str
    Quantity: int
    ReasonNote: str
    UnitOfMeasure: str

class PackagesCreatechangeitemV1RequestItem(TypedDict, total=False):
    Item: str
    Label: str

class PackagesCreatechangelocationV1RequestItem(TypedDict, total=False):
    Label: str
    Location: str
    MoveDate: str
    Sublocation: str

class PackagesCreatefinishV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Label: str

class PackagesCreateplantingsV1RequestItem(TypedDict, total=False):
    LocationName: str
    PackageAdjustmentAmount: int
    PackageAdjustmentUnitOfMeasureName: str
    PackageLabel: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantedDate: str
    StrainName: str
    SublocationName: str
    UnpackagedDate: str

class PackagesCreateplantingsV2RequestItem(TypedDict, total=False):
    LocationName: str
    PackageAdjustmentAmount: int
    PackageAdjustmentUnitOfMeasureName: str
    PackageLabel: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantedDate: str
    StrainName: str
    SublocationName: str
    UnpackagedDate: str

class PackagesCreateremediateV1RequestItem(TypedDict, total=False):
    PackageLabel: str
    RemediationDate: str
    RemediationMethodName: str
    RemediationSteps: str

class PackagesCreatetestingV1RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreatetestingV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreatetestingV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: bool
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreatetestingV2RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreatetestingV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreatetestingV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: List[str]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateunfinishV1RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateadjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    Label: str
    Quantity: int
    ReasonNote: str
    UnitOfMeasure: str

class PackagesUpdatechangenoteV1RequestItem(TypedDict, total=False):
    Note: str
    PackageLabel: str

class PackagesUpdatedecontaminateV2RequestItem(TypedDict, total=False):
    DecontaminationDate: str
    DecontaminationMethodName: str
    DecontaminationSteps: str
    PackageLabel: str

class PackagesUpdatedonationflagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdatedonationunflagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateexternalidV2RequestItem(TypedDict, total=False):
    ExternalId: str
    PackageLabel: str

class PackagesUpdatefinishV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Label: str

class PackagesUpdateitemV2RequestItem(TypedDict, total=False):
    Item: str
    Label: str

class PackagesUpdatelabtestrequiredV2RequestItem(TypedDict, total=False):
    Label: str
    RequiredLabTestBatches: List[str]

class PackagesUpdatelocationV2RequestItem(TypedDict, total=False):
    Label: str
    Location: str
    MoveDate: str
    Sublocation: str

class PackagesUpdatenoteV2RequestItem(TypedDict, total=False):
    Note: str
    PackageLabel: str

class PackagesUpdateremediateV2RequestItem(TypedDict, total=False):
    PackageLabel: str
    RemediationDate: str
    RemediationMethodName: str
    RemediationSteps: str

class PackagesUpdatetradesampleflagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdatetradesampleunflagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateunfinishV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateusebydateV2RequestItem(TypedDict, total=False):
    ExpirationDate: str
    Label: str
    SellByDate: str
    UseByDate: str

class TransportersCreatedriverV2RequestItem(TypedDict, total=False):
    DriversLicenseNumber: str
    EmployeeId: str
    Name: str

class TransportersCreatevehicleV2RequestItem(TypedDict, total=False):
    LicensePlateNumber: str
    Make: str
    Model: str

class TransportersUpdatedriverV2RequestItem(TypedDict, total=False):
    DriversLicenseNumber: str
    EmployeeId: str
    Id: str
    Name: str

class TransportersUpdatevehicleV2RequestItem(TypedDict, total=False):
    Id: str
    LicensePlateNumber: str
    Make: str
    Model: str

class PatientsCreateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class PatientsCreateaddV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class PatientsCreateupdateV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    NewLicenseNumber: str
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class PatientsUpdateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    NewLicenseNumber: str
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class Processing_jobsCreateadjustV1RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreateadjustV1RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentNote: str
    AdjustmentReason: str
    CountUnitOfMeasureName: str
    Id: int
    Packages: List[Processing_jobsCreateadjustV1RequestItem_Packages]
    VolumeUnitOfMeasureName: str
    WeightUnitOfMeasureName: str

class Processing_jobsCreateadjustV2RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreateadjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentNote: str
    AdjustmentReason: str
    CountUnitOfMeasureName: str
    Id: int
    Packages: List[Processing_jobsCreateadjustV2RequestItem_Packages]
    VolumeUnitOfMeasureName: str
    WeightUnitOfMeasureName: str

class Processing_jobsCreatejobtypesV1RequestItem(TypedDict, total=False):
    Attributes: List[str]
    Category: str
    Description: str
    Name: str
    ProcessingSteps: str

class Processing_jobsCreatejobtypesV2RequestItem(TypedDict, total=False):
    Attributes: List[str]
    Category: str
    Description: str
    Name: str
    ProcessingSteps: str

class Processing_jobsCreatestartV1RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreatestartV1RequestItem(TypedDict, total=False):
    CountUnitOfMeasure: str
    JobName: str
    JobType: str
    Packages: List[Processing_jobsCreatestartV1RequestItem_Packages]
    StartDate: str
    VolumeUnitOfMeasure: str
    WeightUnitOfMeasure: str

class Processing_jobsCreatestartV2RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreatestartV2RequestItem(TypedDict, total=False):
    CountUnitOfMeasure: str
    JobName: str
    JobType: str
    Packages: List[Processing_jobsCreatestartV2RequestItem_Packages]
    StartDate: str
    VolumeUnitOfMeasure: str
    WeightUnitOfMeasure: str

class Processing_jobsCreatepackagesV1RequestItem(TypedDict, total=False):
    ExpirationDate: str
    FinishDate: str
    FinishNote: str
    FinishProcessingJob: bool
    Item: str
    JobName: str
    Location: str
    Note: str
    PackageDate: str
    PatientLicenseNumber: str
    ProductionBatchNumber: str
    Quantity: int
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    WasteCountQuantity: str
    WasteCountUnitOfMeasureName: str
    WasteVolumeQuantity: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightQuantity: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsCreatepackagesV2RequestItem(TypedDict, total=False):
    ExpirationDate: str
    FinishDate: str
    FinishNote: str
    FinishProcessingJob: bool
    Item: str
    JobName: str
    Location: str
    Note: str
    PackageDate: str
    PatientLicenseNumber: str
    ProductionBatchNumber: str
    Quantity: int
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    WasteCountQuantity: str
    WasteCountUnitOfMeasureName: str
    WasteVolumeQuantity: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightQuantity: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsUpdatefinishV1RequestItem(TypedDict, total=False):
    FinishDate: str
    FinishNote: str
    Id: int
    TotalCountWaste: str
    TotalVolumeWaste: str
    TotalWeightWaste: int
    WasteCountUnitOfMeasureName: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsUpdatefinishV2RequestItem(TypedDict, total=False):
    FinishDate: str
    FinishNote: str
    Id: int
    TotalCountWaste: str
    TotalVolumeWaste: str
    TotalWeightWaste: int
    WasteCountUnitOfMeasureName: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsUpdatejobtypesV1RequestItem(TypedDict, total=False):
    Attributes: List[str]
    CategoryName: str
    Description: str
    Id: int
    Name: str
    ProcessingSteps: str

class Processing_jobsUpdatejobtypesV2RequestItem(TypedDict, total=False):
    Attributes: List[str]
    CategoryName: str
    Description: str
    Id: int
    Name: str
    ProcessingSteps: str

class Processing_jobsUpdateunfinishV1RequestItem(TypedDict, total=False):
    Id: int

class Processing_jobsUpdateunfinishV2RequestItem(TypedDict, total=False):
    Id: int

class Retail_idCreateassociateV2RequestItem(TypedDict, total=False):
    PackageLabel: str
    QrUrls: List[str]

class Retail_idCreategenerateV2Request(TypedDict, total=False):
    PackageLabel: str
    Quantity: int

class Retail_idCreatemergeV2Request(TypedDict, total=False):
    packageLabels: List[str]

class Retail_idCreatepackageinfoV2Request(TypedDict, total=False):
    packageLabels: List[str]

class SalesCreatedeliveryV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatedeliveryV1RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreatedeliveryV1RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreatedeliveryV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatedeliveryV2RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreatedeliveryV2RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreatedeliveryretailerV1RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatedeliveryretailerV1RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    EstimatedArrivalDateTime: str
    PatientLicenseNumber: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    Transactions: List[SalesCreatedeliveryretailerV1RequestItem_Destinations_Transactions]

class SalesCreatedeliveryretailerV1RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreatedeliveryretailerV1RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesCreatedeliveryretailerV1RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreatedeliveryretailerV1RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreatedeliveryretailerV2RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatedeliveryretailerV2RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    EstimatedArrivalDateTime: str
    PatientLicenseNumber: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    Transactions: List[SalesCreatedeliveryretailerV2RequestItem_Destinations_Transactions]

class SalesCreatedeliveryretailerV2RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreatedeliveryretailerV2RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesCreatedeliveryretailerV2RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreatedeliveryretailerV2RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreatedeliveryretailerdepartV1RequestItem(TypedDict, total=False):
    RetailerDeliveryId: int

class SalesCreatedeliveryretailerdepartV2RequestItem(TypedDict, total=False):
    RetailerDeliveryId: int

class SalesCreatedeliveryretailerendV1RequestItem_Packages(TypedDict, total=False):
    EndQuantity: int
    EndUnitOfMeasure: str
    Label: str

class SalesCreatedeliveryretailerendV1RequestItem(TypedDict, total=False):
    ActualArrivalDateTime: str
    Packages: List[SalesCreatedeliveryretailerendV1RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreatedeliveryretailerendV2RequestItem_Packages(TypedDict, total=False):
    EndQuantity: int
    EndUnitOfMeasure: str
    Label: str

class SalesCreatedeliveryretailerendV2RequestItem(TypedDict, total=False):
    ActualArrivalDateTime: str
    Packages: List[SalesCreatedeliveryretailerendV2RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreatedeliveryretailerrestockV1RequestItem_Packages(TypedDict, total=False):
    PackageLabel: str
    Quantity: int
    RemoveCurrentPackage: bool
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreatedeliveryretailerrestockV1RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreatedeliveryretailerrestockV1RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreatedeliveryretailerrestockV2RequestItem_Packages(TypedDict, total=False):
    PackageLabel: str
    Quantity: int
    RemoveCurrentPackage: bool
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreatedeliveryretailerrestockV2RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreatedeliveryretailerrestockV2RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreatedeliveryretailersaleV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatedeliveryretailersaleV1RequestItem(TypedDict, total=False):
    ConsumerId: int
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    RetailerDeliveryId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreatedeliveryretailersaleV1RequestItem_Transactions]

class SalesCreatedeliveryretailersaleV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatedeliveryretailersaleV2RequestItem(TypedDict, total=False):
    ConsumerId: int
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    RetailerDeliveryId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreatedeliveryretailersaleV2RequestItem_Transactions]

class SalesCreatereceiptV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatereceiptV1RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreatereceiptV1RequestItem_Transactions]

class SalesCreatereceiptV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreatereceiptV2RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreatereceiptV2RequestItem_Transactions]

class SalesCreatetransactionbydateV1RequestItem(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatedeliveryV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatedeliveryV1RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdatedeliveryV1RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliveryV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatedeliveryV2RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdatedeliveryV2RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliverycompleteV1RequestItem_Returnedpackages(TypedDict, total=False):
    Label: str
    ReturnQuantityVerified: int
    ReturnReason: str
    ReturnReasonNote: str
    ReturnUnitOfMeasure: str

class SalesUpdatedeliverycompleteV1RequestItem(TypedDict, total=False):
    AcceptedPackages: List[str]
    ActualArrivalDateTime: str
    Id: int
    PaymentType: str
    ReturnedPackages: List[SalesUpdatedeliverycompleteV1RequestItem_Returnedpackages]

class SalesUpdatedeliverycompleteV2RequestItem_Returnedpackages(TypedDict, total=False):
    Label: str
    ReturnQuantityVerified: int
    ReturnReason: str
    ReturnReasonNote: str
    ReturnUnitOfMeasure: str

class SalesUpdatedeliverycompleteV2RequestItem(TypedDict, total=False):
    AcceptedPackages: List[str]
    ActualArrivalDateTime: str
    Id: int
    PaymentType: str
    ReturnedPackages: List[SalesUpdatedeliverycompleteV2RequestItem_Returnedpackages]

class SalesUpdatedeliveryhubV1RequestItem(TypedDict, total=False):
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PhoneNumberForQuestions: str
    PlannedRoute: str
    TransporterFacilityId: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliveryhubV2RequestItem(TypedDict, total=False):
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PhoneNumberForQuestions: str
    PlannedRoute: str
    TransporterFacilityId: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliveryhubacceptV1RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdatedeliveryhubacceptV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdatedeliveryhubdepartV1RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdatedeliveryhubdepartV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdatedeliveryhubverifyidV1RequestItem(TypedDict, total=False):
    Id: int
    PaymentType: str

class SalesUpdatedeliveryhubverifyidV2RequestItem(TypedDict, total=False):
    Id: int
    PaymentType: str

class SalesUpdatedeliveryretailerV1RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatedeliveryretailerV1RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    DriverEmployeeId: int
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdatedeliveryretailerV1RequestItem_Destinations_Transactions]
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliveryretailerV1RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesUpdatedeliveryretailerV1RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesUpdatedeliveryretailerV1RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Id: int
    Packages: List[SalesUpdatedeliveryretailerV1RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliveryretailerV2RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatedeliveryretailerV2RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    DriverEmployeeId: int
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdatedeliveryretailerV2RequestItem_Destinations_Transactions]
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatedeliveryretailerV2RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesUpdatedeliveryretailerV2RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesUpdatedeliveryretailerV2RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Id: int
    Packages: List[SalesUpdatedeliveryretailerV2RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdatereceiptV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatereceiptV1RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    Id: int
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdatereceiptV1RequestItem_Transactions]

class SalesUpdatereceiptV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdatereceiptV2RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    Id: int
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdatereceiptV2RequestItem_Transactions]

class SalesUpdatereceiptfinalizeV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdatereceiptunfinalizeV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdatetransactionbydateV1RequestItem(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class Patient_check_insCreateV1RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Patient_check_insCreateV2RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Patient_check_insUpdateV1RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    Id: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Patient_check_insUpdateV2RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    Id: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Plant_batchesCreateadditivesV1RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Plant_batchesCreateadditivesV1RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Plant_batchesCreateadditivesV1RequestItem_Activeingredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantBatchName: str
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class Plant_batchesCreateadditivesV2RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Plant_batchesCreateadditivesV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Plant_batchesCreateadditivesV2RequestItem_Activeingredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantBatchName: str
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class Plant_batchesCreateadditivesusingtemplateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    AdditivesTemplateName: str
    PlantBatchName: str
    Rate: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str
    Volume: str

class Plant_batchesCreateadjustV1RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    PlantBatchName: str
    Quantity: int
    ReasonNote: str

class Plant_batchesCreateadjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    PlantBatchName: str
    Quantity: int
    ReasonNote: str

class Plant_batchesCreatechangegrowthphaseV1RequestItem(TypedDict, total=False):
    Count: int
    CountPerPlant: str
    GrowthDate: str
    GrowthPhase: str
    Name: str
    NewLocation: str
    NewSublocation: str
    PatientLicenseNumber: str
    StartingTag: str

class Plant_batchesCreategrowthphaseV2RequestItem(TypedDict, total=False):
    Count: int
    CountPerPlant: str
    GrowthDate: str
    GrowthPhase: str
    Name: str
    NewLocation: str
    NewSublocation: str
    PatientLicenseNumber: str
    StartingTag: str

class Plant_batchesCreatepackageV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreatepackagefrommotherplantV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreatepackagefrommotherplantV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreateplantingsV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    Location: str
    Name: str
    PatientLicenseNumber: str
    SourcePlantBatches: str
    Strain: str
    Sublocation: str
    Type: str

class Plant_batchesCreatesplitV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    GroupName: str
    Location: str
    PatientLicenseNumber: str
    PlantBatch: str
    Strain: str
    Sublocation: str

class Plant_batchesCreatesplitV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    GroupName: str
    Location: str
    PatientLicenseNumber: str
    PlantBatch: str
    Strain: str
    Sublocation: str

class Plant_batchesCreatewasteV1RequestItem(TypedDict, total=False):
    MixedMaterial: str
    Note: str
    PlantBatchName: str
    ReasonName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class Plant_batchesCreatewasteV2RequestItem(TypedDict, total=False):
    MixedMaterial: str
    Note: str
    PlantBatchName: str
    ReasonName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class Plant_batchesCreatepackagesV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreateplantingsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    Location: str
    Name: str
    PatientLicenseNumber: str
    SourcePlantBatches: str
    Strain: str
    Sublocation: str
    Type: str

class Plant_batchesUpdatelocationV2RequestItem(TypedDict, total=False):
    Location: str
    MoveDate: str
    Name: str
    Sublocation: str

class Plant_batchesUpdatemoveplantbatchesV1RequestItem(TypedDict, total=False):
    Location: str
    MoveDate: str
    Name: str
    Sublocation: str

class Plant_batchesUpdatenameV2RequestItem(TypedDict, total=False):
    Group: str
    Id: int
    NewGroup: str

class Plant_batchesUpdatestrainV2RequestItem(TypedDict, total=False):
    Id: int
    Name: str
    StrainId: int
    StrainName: str

class Plant_batchesUpdatetagV2RequestItem(TypedDict, total=False):
    Group: str
    Id: int
    NewTag: str
    ReplaceDate: str
    TagId: int

class PlantsCreateadditivesV1RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateadditivesV1RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateadditivesV1RequestItem_Activeingredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantLabels: List[str]
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateadditivesV2RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateadditivesV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateadditivesV2RequestItem_Activeingredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantLabels: List[str]
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateadditivesbylocationV1RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateadditivesbylocationV1RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateadditivesbylocationV1RequestItem_Activeingredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    LocationName: str
    ProductSupplier: str
    ProductTradeName: str
    SublocationName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateadditivesbylocationV2RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateadditivesbylocationV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateadditivesbylocationV2RequestItem_Activeingredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    LocationName: str
    ProductSupplier: str
    ProductTradeName: str
    SublocationName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateadditivesbylocationusingtemplateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    AdditivesTemplateName: str
    LocationName: str
    Rate: str
    SublocationName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str
    Volume: str

class PlantsCreateadditivesusingtemplateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    AdditivesTemplateName: str
    PlantLabels: List[str]
    Rate: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str
    Volume: str

class PlantsCreatechangegrowthphasesV1RequestItem(TypedDict, total=False):
    GrowthDate: str
    GrowthPhase: str
    Id: int
    Label: str
    NewLocation: str
    NewSublocation: str
    NewTag: str

class PlantsCreateharvestplantsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    UnitOfWeight: str
    Weight: float

class PlantsCreatemanicureV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    PlantCount: int
    UnitOfWeight: str
    Weight: float

class PlantsCreatemanicureplantsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    PlantCount: int
    UnitOfWeight: str
    Weight: float

class PlantsCreatemoveplantsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    Label: str
    Location: str
    Sublocation: str

class PlantsCreateplantbatchpackageV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PackageTag: str
    PatientLicenseNumber: str
    PlantBatchType: str
    PlantLabel: str
    Sublocation: str

class PlantsCreateplantbatchpackageV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PackageTag: str
    PatientLicenseNumber: str
    PlantBatchType: str
    PlantLabel: str
    Sublocation: str

class PlantsCreateplantingsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    LocationName: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantLabel: str
    StrainName: str
    SublocationName: str

class PlantsCreateplantingsV2RequestItem(TypedDict, total=False):
    ActualDate: str
    LocationName: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantLabel: str
    StrainName: str
    SublocationName: str

class PlantsCreatewasteV1RequestItem(TypedDict, total=False):
    LocationName: str
    MixedMaterial: str
    Note: str
    PlantLabels: List[Any]
    ReasonName: str
    SublocationName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class PlantsCreatewasteV2RequestItem(TypedDict, total=False):
    LocationName: str
    MixedMaterial: str
    Note: str
    PlantLabels: List[Any]
    ReasonName: str
    SublocationName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class PlantsUpdateadjustV2RequestItem(TypedDict, total=False):
    AdjustCount: int
    AdjustReason: str
    AdjustmentDate: str
    Id: int
    Label: str
    ReasonNote: str

class PlantsUpdategrowthphaseV2RequestItem(TypedDict, total=False):
    GrowthDate: str
    GrowthPhase: str
    Id: int
    Label: str
    NewLocation: str
    NewSublocation: str
    NewTag: str

class PlantsUpdateharvestV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    UnitOfWeight: str
    Weight: float

class PlantsUpdatelocationV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    Label: str
    Location: str
    Sublocation: str

class PlantsUpdatemergeV2RequestItem(TypedDict, total=False):
    MergeDate: str
    SourcePlantGroupLabel: str
    TargetPlantGroupLabel: str

class PlantsUpdatesplitV2RequestItem(TypedDict, total=False):
    PlantCount: int
    SourcePlantLabel: str
    SplitDate: str
    StrainLabel: str
    TagLabel: str

class PlantsUpdatestrainV2RequestItem(TypedDict, total=False):
    Id: int
    Label: str
    StrainId: int
    StrainName: str

class PlantsUpdatetagV2RequestItem(TypedDict, total=False):
    Id: int
    Label: str
    NewTag: str
    ReplaceDate: str
    TagId: int

class SublocationsCreateV2RequestItem(TypedDict, total=False):
    Name: str

class SublocationsUpdateV2RequestItem(TypedDict, total=False):
    Id: int
    Name: str

class Additives_templatesCreateV2RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Additives_templatesCreateV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Additives_templatesCreateV2RequestItem_Activeingredients]
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    Name: str
    Note: str
    ProductSupplier: str
    ProductTradeName: str
    RestrictiveEntryIntervalQuantityDescription: str
    RestrictiveEntryIntervalTimeDescription: str

class Additives_templatesUpdateV2RequestItem_Activeingredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Additives_templatesUpdateV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Additives_templatesUpdateV2RequestItem_Activeingredients]
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    Id: int
    Name: str
    Note: str
    ProductSupplier: str
    ProductTradeName: str
    RestrictiveEntryIntervalQuantityDescription: str
    RestrictiveEntryIntervalTimeDescription: str

class StrainsCreateV1RequestItem(TypedDict, total=False):
    CbdLevel: float
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class StrainsCreateV2RequestItem(TypedDict, total=False):
    CbdLevel: float
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class StrainsCreateupdateV1RequestItem(TypedDict, total=False):
    CbdLevel: float
    Id: int
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class StrainsUpdateV2RequestItem(TypedDict, total=False):
    CbdLevel: float
    Id: int
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class TransfersCreateexternalincomingV1RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersCreateexternalincomingV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateexternalincomingV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersCreateexternalincomingV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreateexternalincomingV1RequestItem_Destinations_Transporters]

class TransfersCreateexternalincomingV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreateexternalincomingV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateexternalincomingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersCreateexternalincomingV2RequestItem_Destinations_Transporters_Transporterdetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateexternalincomingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersCreateexternalincomingV2RequestItem_Destinations_Transporters_Transporterdetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateexternalincomingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersCreateexternalincomingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreateexternalincomingV2RequestItem_Destinations_Transporters]

class TransfersCreateexternalincomingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreateexternalincomingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreatetemplatesV1RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersCreatetemplatesV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreatetemplatesV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersCreatetemplatesV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreatetemplatesV1RequestItem_Destinations_Transporters]

class TransfersCreatetemplatesV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreatetemplatesV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreatetemplatesoutgoingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersCreatetemplatesoutgoingV2RequestItem_Destinations_Transporters_Transporterdetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreatetemplatesoutgoingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersCreatetemplatesoutgoingV2RequestItem_Destinations_Transporters_Transporterdetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreatetemplatesoutgoingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersCreatetemplatesoutgoingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreatetemplatesoutgoingV2RequestItem_Destinations_Transporters]

class TransfersCreatetemplatesoutgoingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreatetemplatesoutgoingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateexternalincomingV1RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersUpdateexternalincomingV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateexternalincomingV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersUpdateexternalincomingV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdateexternalincomingV1RequestItem_Destinations_Transporters]

class TransfersUpdateexternalincomingV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdateexternalincomingV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransferId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateexternalincomingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersUpdateexternalincomingV2RequestItem_Destinations_Transporters_Transporterdetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateexternalincomingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersUpdateexternalincomingV2RequestItem_Destinations_Transporters_Transporterdetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateexternalincomingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersUpdateexternalincomingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdateexternalincomingV2RequestItem_Destinations_Transporters]

class TransfersUpdateexternalincomingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdateexternalincomingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransferId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdatetemplatesV1RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersUpdatetemplatesV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdatetemplatesV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersUpdatetemplatesV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdatetemplatesV1RequestItem_Destinations_Transporters]

class TransfersUpdatetemplatesV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdatetemplatesV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransferTemplateId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations_Transporters_Transporterdetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations_Transporters_Transporterdetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations_Transporters]

class TransfersUpdatetemplatesoutgoingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdatetemplatesoutgoingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransferTemplateId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class HarvestsCreatefinishV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int

class HarvestsCreatepackageV1RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatepackageV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatepackageV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreatepackageV2RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatepackageV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatepackageV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreatepackagetestingV1RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatepackagetestingV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatepackagetestingV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreatepackagetestingV2RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatepackagetestingV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatepackagetestingV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreateremovewasteV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    UnitOfWeight: str
    WasteType: str
    WasteWeight: float

class HarvestsCreateunfinishV1RequestItem(TypedDict, total=False):
    Id: int

class HarvestsCreatewasteV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    UnitOfWeight: str
    WasteType: str
    WasteWeight: float

class HarvestsUpdatefinishV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int

class HarvestsUpdatelocationV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    Id: int

class HarvestsUpdatemoveV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    Id: int

class HarvestsUpdaterenameV1RequestItem(TypedDict, total=False):
    Id: int
    NewName: str
    OldName: str

class HarvestsUpdaterenameV2RequestItem(TypedDict, total=False):
    Id: int
    NewName: str
    OldName: str

class HarvestsUpdaterestoreharvestedplantsV2RequestItem(TypedDict, total=False):
    HarvestId: int
    PlantTags: List[str]

class HarvestsUpdateunfinishV2RequestItem(TypedDict, total=False):
    Id: int

class ItemsCreateV1RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsCreateV2RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsCreatebrandV2RequestItem(TypedDict, total=False):
    Name: str

class ItemsCreatefileV2RequestItem(TypedDict, total=False):
    EncodedImageBase64: str
    FileName: str

class ItemsCreatephotoV1RequestItem(TypedDict, total=False):
    EncodedImageBase64: str
    FileName: str

class ItemsCreatephotoV2RequestItem(TypedDict, total=False):
    EncodedImageBase64: str
    FileName: str

class ItemsCreateupdateV1RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    Id: int
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsUpdateV2RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    Id: int
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsUpdatebrandV2RequestItem(TypedDict, total=False):
    Id: int
    Name: str



class MetrcClient:
    def __init__(self, base_url: str, vendor_key: str, user_key: str, client: Optional[httpx.Client] = None):
        self.base_url = base_url.rstrip('/')
        self.vendor_key = vendor_key
        self.user_key = user_key
        self.client = client or httpx.Client()
        self.client.auth = (vendor_key, user_key)

    def _send(self, method: str, path: str, body: Any = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self.client.request(method, url, json=body)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def lab_tests_createrecord_v1(self, body: Optional[List[Lab_testsCreaterecordV1RequestItem]] = None) -> Any:
        path = f"/labtests/v1/record"
        return self._send("POST", path, body)

    def lab_tests_createrecord_v2(self, body: Optional[List[Lab_testsCreaterecordV2RequestItem]] = None) -> Any:
        path = f"/labtests/v2/record"
        return self._send("POST", path, body)

    def lab_tests_getbatches_v2(self, body: Any = None) -> Any:
        path = f"/labtests/v2/batches"
        return self._send("GET", path, body)

    def lab_tests_getlabtestdocument_v1(self, id: str, body: Any = None) -> Any:
        path = f"/labtests/v1/labtestdocument/{id}"
        return self._send("GET", path, body)

    def lab_tests_getlabtestdocument_v2(self, id: str, body: Any = None) -> Any:
        path = f"/labtests/v2/labtestdocument/{id}"
        return self._send("GET", path, body)

    def lab_tests_getresults_v1(self, body: Any = None) -> Any:
        path = f"/labtests/v1/results"
        return self._send("GET", path, body)

    def lab_tests_getresults_v2(self, body: Any = None) -> Any:
        path = f"/labtests/v2/results"
        return self._send("GET", path, body)

    def lab_tests_getstates_v1(self, body: Any = None) -> Any:
        path = f"/labtests/v1/states"
        return self._send("GET", path, body)

    def lab_tests_getstates_v2(self, body: Any = None) -> Any:
        path = f"/labtests/v2/states"
        return self._send("GET", path, body)

    def lab_tests_gettypes_v1(self, body: Any = None) -> Any:
        path = f"/labtests/v1/types"
        return self._send("GET", path, body)

    def lab_tests_gettypes_v2(self, body: Any = None) -> Any:
        path = f"/labtests/v2/types"
        return self._send("GET", path, body)

    def lab_tests_updatelabtestdocument_v1(self, body: Optional[List[Lab_testsUpdatelabtestdocumentV1RequestItem]] = None) -> Any:
        path = f"/labtests/v1/labtestdocument"
        return self._send("PUT", path, body)

    def lab_tests_updatelabtestdocument_v2(self, body: Optional[List[Lab_testsUpdatelabtestdocumentV2RequestItem]] = None) -> Any:
        path = f"/labtests/v2/labtestdocument"
        return self._send("PUT", path, body)

    def lab_tests_updateresultrelease_v1(self, body: Optional[List[Lab_testsUpdateresultreleaseV1RequestItem]] = None) -> Any:
        path = f"/labtests/v1/results/release"
        return self._send("PUT", path, body)

    def lab_tests_updateresultrelease_v2(self, body: Optional[List[Lab_testsUpdateresultreleaseV2RequestItem]] = None) -> Any:
        path = f"/labtests/v2/results/release"
        return self._send("PUT", path, body)

    def locations_create_v1(self, body: Optional[List[LocationsCreateV1RequestItem]] = None) -> Any:
        path = f"/locations/v1/create"
        return self._send("POST", path, body)

    def locations_create_v2(self, body: Optional[List[LocationsCreateV2RequestItem]] = None) -> Any:
        path = f"/locations/v2"
        return self._send("POST", path, body)

    def locations_createupdate_v1(self, body: Optional[List[LocationsCreateupdateV1RequestItem]] = None) -> Any:
        path = f"/locations/v1/update"
        return self._send("POST", path, body)

    def locations_delete_v1(self, id: str, body: Any = None) -> Any:
        path = f"/locations/v1/{id}"
        return self._send("DELETE", path, body)

    def locations_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/locations/v2/{id}"
        return self._send("DELETE", path, body)

    def locations_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/locations/v1/{id}"
        return self._send("GET", path, body)

    def locations_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/locations/v2/{id}"
        return self._send("GET", path, body)

    def locations_getactive_v1(self, body: Any = None) -> Any:
        path = f"/locations/v1/active"
        return self._send("GET", path, body)

    def locations_getactive_v2(self, body: Any = None) -> Any:
        path = f"/locations/v2/active"
        return self._send("GET", path, body)

    def locations_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/locations/v2/inactive"
        return self._send("GET", path, body)

    def locations_gettypes_v1(self, body: Any = None) -> Any:
        path = f"/locations/v1/types"
        return self._send("GET", path, body)

    def locations_gettypes_v2(self, body: Any = None) -> Any:
        path = f"/locations/v2/types"
        return self._send("GET", path, body)

    def locations_update_v2(self, body: Optional[List[LocationsUpdateV2RequestItem]] = None) -> Any:
        path = f"/locations/v2"
        return self._send("PUT", path, body)

    def packages_create_v1(self, body: Optional[List[PackagesCreateV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/create"
        return self._send("POST", path, body)

    def packages_create_v2(self, body: Optional[List[PackagesCreateV2RequestItem]] = None) -> Any:
        path = f"/packages/v2"
        return self._send("POST", path, body)

    def packages_createadjust_v1(self, body: Optional[List[PackagesCreateadjustV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/adjust"
        return self._send("POST", path, body)

    def packages_createadjust_v2(self, body: Optional[List[PackagesCreateadjustV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/adjust"
        return self._send("POST", path, body)

    def packages_createchangeitem_v1(self, body: Optional[List[PackagesCreatechangeitemV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/change/item"
        return self._send("POST", path, body)

    def packages_createchangelocation_v1(self, body: Optional[List[PackagesCreatechangelocationV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/change/locations"
        return self._send("POST", path, body)

    def packages_createfinish_v1(self, body: Optional[List[PackagesCreatefinishV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/finish"
        return self._send("POST", path, body)

    def packages_createplantings_v1(self, body: Optional[List[PackagesCreateplantingsV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/create/plantings"
        return self._send("POST", path, body)

    def packages_createplantings_v2(self, body: Optional[List[PackagesCreateplantingsV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/plantings"
        return self._send("POST", path, body)

    def packages_createremediate_v1(self, body: Optional[List[PackagesCreateremediateV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/remediate"
        return self._send("POST", path, body)

    def packages_createtesting_v1(self, body: Optional[List[PackagesCreatetestingV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/create/testing"
        return self._send("POST", path, body)

    def packages_createtesting_v2(self, body: Optional[List[PackagesCreatetestingV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/testing"
        return self._send("POST", path, body)

    def packages_createunfinish_v1(self, body: Optional[List[PackagesCreateunfinishV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/unfinish"
        return self._send("POST", path, body)

    def packages_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/packages/v2/{id}"
        return self._send("DELETE", path, body)

    def packages_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/packages/v1/{id}"
        return self._send("GET", path, body)

    def packages_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/packages/v2/{id}"
        return self._send("GET", path, body)

    def packages_getactive_v1(self, body: Any = None) -> Any:
        path = f"/packages/v1/active"
        return self._send("GET", path, body)

    def packages_getactive_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/active"
        return self._send("GET", path, body)

    def packages_getadjustreasons_v1(self, body: Any = None) -> Any:
        path = f"/packages/v1/adjust/reasons"
        return self._send("GET", path, body)

    def packages_getadjustreasons_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/adjust/reasons"
        return self._send("GET", path, body)

    def packages_getbylabel_v1(self, label: str, body: Any = None) -> Any:
        path = f"/packages/v1/{label}"
        return self._send("GET", path, body)

    def packages_getbylabel_v2(self, label: str, body: Any = None) -> Any:
        path = f"/packages/v2/{label}"
        return self._send("GET", path, body)

    def packages_getinactive_v1(self, body: Any = None) -> Any:
        path = f"/packages/v1/inactive"
        return self._send("GET", path, body)

    def packages_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/inactive"
        return self._send("GET", path, body)

    def packages_getintransit_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/intransit"
        return self._send("GET", path, body)

    def packages_getlabsamples_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/labsamples"
        return self._send("GET", path, body)

    def packages_getonhold_v1(self, body: Any = None) -> Any:
        path = f"/packages/v1/onhold"
        return self._send("GET", path, body)

    def packages_getonhold_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/onhold"
        return self._send("GET", path, body)

    def packages_getsourceharvest_v2(self, id: str, body: Any = None) -> Any:
        path = f"/packages/v2/{id}/source/harvests"
        return self._send("GET", path, body)

    def packages_gettransferred_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/transferred"
        return self._send("GET", path, body)

    def packages_gettypes_v1(self, body: Any = None) -> Any:
        path = f"/packages/v1/types"
        return self._send("GET", path, body)

    def packages_gettypes_v2(self, body: Any = None) -> Any:
        path = f"/packages/v2/types"
        return self._send("GET", path, body)

    def packages_updateadjust_v2(self, body: Optional[List[PackagesUpdateadjustV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/adjust"
        return self._send("PUT", path, body)

    def packages_updatechangenote_v1(self, body: Optional[List[PackagesUpdatechangenoteV1RequestItem]] = None) -> Any:
        path = f"/packages/v1/change/note"
        return self._send("PUT", path, body)

    def packages_updatedecontaminate_v2(self, body: Optional[List[PackagesUpdatedecontaminateV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/decontaminate"
        return self._send("PUT", path, body)

    def packages_updatedonationflag_v2(self, body: Optional[List[PackagesUpdatedonationflagV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/donation/flag"
        return self._send("PUT", path, body)

    def packages_updatedonationunflag_v2(self, body: Optional[List[PackagesUpdatedonationunflagV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/donation/unflag"
        return self._send("PUT", path, body)

    def packages_updateexternalid_v2(self, body: Optional[List[PackagesUpdateexternalidV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/externalid"
        return self._send("PUT", path, body)

    def packages_updatefinish_v2(self, body: Optional[List[PackagesUpdatefinishV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/finish"
        return self._send("PUT", path, body)

    def packages_updateitem_v2(self, body: Optional[List[PackagesUpdateitemV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/item"
        return self._send("PUT", path, body)

    def packages_updatelabtestrequired_v2(self, body: Optional[List[PackagesUpdatelabtestrequiredV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/labtests/required"
        return self._send("PUT", path, body)

    def packages_updatelocation_v2(self, body: Optional[List[PackagesUpdatelocationV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/location"
        return self._send("PUT", path, body)

    def packages_updatenote_v2(self, body: Optional[List[PackagesUpdatenoteV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/note"
        return self._send("PUT", path, body)

    def packages_updateremediate_v2(self, body: Optional[List[PackagesUpdateremediateV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/remediate"
        return self._send("PUT", path, body)

    def packages_updatetradesampleflag_v2(self, body: Optional[List[PackagesUpdatetradesampleflagV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/tradesample/flag"
        return self._send("PUT", path, body)

    def packages_updatetradesampleunflag_v2(self, body: Optional[List[PackagesUpdatetradesampleunflagV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/tradesample/unflag"
        return self._send("PUT", path, body)

    def packages_updateunfinish_v2(self, body: Optional[List[PackagesUpdateunfinishV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/unfinish"
        return self._send("PUT", path, body)

    def packages_updateusebydate_v2(self, body: Optional[List[PackagesUpdateusebydateV2RequestItem]] = None) -> Any:
        path = f"/packages/v2/usebydate"
        return self._send("PUT", path, body)

    def sandbox_createintegratorsetup_v2(self, body: Any = None) -> Any:
        path = f"/sandbox/v2/integrator/setup"
        return self._send("POST", path, body)

    def transporters_createdriver_v2(self, body: Optional[List[TransportersCreatedriverV2RequestItem]] = None) -> Any:
        path = f"/transporters/v2/drivers"
        return self._send("POST", path, body)

    def transporters_createvehicle_v2(self, body: Optional[List[TransportersCreatevehicleV2RequestItem]] = None) -> Any:
        path = f"/transporters/v2/vehicles"
        return self._send("POST", path, body)

    def transporters_deletedriver_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transporters/v2/drivers/{id}"
        return self._send("DELETE", path, body)

    def transporters_deletevehicle_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transporters/v2/vehicles/{id}"
        return self._send("DELETE", path, body)

    def transporters_getdriver_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transporters/v2/drivers/{id}"
        return self._send("GET", path, body)

    def transporters_getdrivers_v2(self, body: Any = None) -> Any:
        path = f"/transporters/v2/drivers"
        return self._send("GET", path, body)

    def transporters_getvehicle_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transporters/v2/vehicles/{id}"
        return self._send("GET", path, body)

    def transporters_getvehicles_v2(self, body: Any = None) -> Any:
        path = f"/transporters/v2/vehicles"
        return self._send("GET", path, body)

    def transporters_updatedriver_v2(self, body: Optional[List[TransportersUpdatedriverV2RequestItem]] = None) -> Any:
        path = f"/transporters/v2/drivers"
        return self._send("PUT", path, body)

    def transporters_updatevehicle_v2(self, body: Optional[List[TransportersUpdatevehicleV2RequestItem]] = None) -> Any:
        path = f"/transporters/v2/vehicles"
        return self._send("PUT", path, body)

    def patients_create_v2(self, body: Optional[List[PatientsCreateV2RequestItem]] = None) -> Any:
        path = f"/patients/v2"
        return self._send("POST", path, body)

    def patients_createadd_v1(self, body: Optional[List[PatientsCreateaddV1RequestItem]] = None) -> Any:
        path = f"/patients/v1/add"
        return self._send("POST", path, body)

    def patients_createupdate_v1(self, body: Optional[List[PatientsCreateupdateV1RequestItem]] = None) -> Any:
        path = f"/patients/v1/update"
        return self._send("POST", path, body)

    def patients_delete_v1(self, id: str, body: Any = None) -> Any:
        path = f"/patients/v1/{id}"
        return self._send("DELETE", path, body)

    def patients_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/patients/v2/{id}"
        return self._send("DELETE", path, body)

    def patients_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/patients/v1/{id}"
        return self._send("GET", path, body)

    def patients_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/patients/v2/{id}"
        return self._send("GET", path, body)

    def patients_getactive_v1(self, body: Any = None) -> Any:
        path = f"/patients/v1/active"
        return self._send("GET", path, body)

    def patients_getactive_v2(self, body: Any = None) -> Any:
        path = f"/patients/v2/active"
        return self._send("GET", path, body)

    def patients_update_v2(self, body: Optional[List[PatientsUpdateV2RequestItem]] = None) -> Any:
        path = f"/patients/v2"
        return self._send("PUT", path, body)

    def processing_jobs_createadjust_v1(self, body: Optional[List[Processing_jobsCreateadjustV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/adjust"
        return self._send("POST", path, body)

    def processing_jobs_createadjust_v2(self, body: Optional[List[Processing_jobsCreateadjustV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/adjust"
        return self._send("POST", path, body)

    def processing_jobs_createjobtypes_v1(self, body: Optional[List[Processing_jobsCreatejobtypesV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/jobtypes"
        return self._send("POST", path, body)

    def processing_jobs_createjobtypes_v2(self, body: Optional[List[Processing_jobsCreatejobtypesV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/jobtypes"
        return self._send("POST", path, body)

    def processing_jobs_createstart_v1(self, body: Optional[List[Processing_jobsCreatestartV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/start"
        return self._send("POST", path, body)

    def processing_jobs_createstart_v2(self, body: Optional[List[Processing_jobsCreatestartV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/start"
        return self._send("POST", path, body)

    def processing_jobs_createpackages_v1(self, body: Optional[List[Processing_jobsCreatepackagesV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/createpackages"
        return self._send("POST", path, body)

    def processing_jobs_createpackages_v2(self, body: Optional[List[Processing_jobsCreatepackagesV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/createpackages"
        return self._send("POST", path, body)

    def processing_jobs_delete_v1(self, id: str, body: Any = None) -> Any:
        path = f"/processing/v1/{id}"
        return self._send("DELETE", path, body)

    def processing_jobs_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/processing/v2/{id}"
        return self._send("DELETE", path, body)

    def processing_jobs_deletejobtypes_v1(self, id: str, body: Any = None) -> Any:
        path = f"/processing/v1/jobtypes/{id}"
        return self._send("DELETE", path, body)

    def processing_jobs_deletejobtypes_v2(self, id: str, body: Any = None) -> Any:
        path = f"/processing/v2/jobtypes/{id}"
        return self._send("DELETE", path, body)

    def processing_jobs_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/processing/v1/{id}"
        return self._send("GET", path, body)

    def processing_jobs_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/processing/v2/{id}"
        return self._send("GET", path, body)

    def processing_jobs_getactive_v1(self, body: Any = None) -> Any:
        path = f"/processing/v1/active"
        return self._send("GET", path, body)

    def processing_jobs_getactive_v2(self, body: Any = None) -> Any:
        path = f"/processing/v2/active"
        return self._send("GET", path, body)

    def processing_jobs_getinactive_v1(self, body: Any = None) -> Any:
        path = f"/processing/v1/inactive"
        return self._send("GET", path, body)

    def processing_jobs_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/processing/v2/inactive"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypesactive_v1(self, body: Any = None) -> Any:
        path = f"/processing/v1/jobtypes/active"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypesactive_v2(self, body: Any = None) -> Any:
        path = f"/processing/v2/jobtypes/active"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypesattributes_v1(self, body: Any = None) -> Any:
        path = f"/processing/v1/jobtypes/attributes"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypesattributes_v2(self, body: Any = None) -> Any:
        path = f"/processing/v2/jobtypes/attributes"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypescategories_v1(self, body: Any = None) -> Any:
        path = f"/processing/v1/jobtypes/categories"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypescategories_v2(self, body: Any = None) -> Any:
        path = f"/processing/v2/jobtypes/categories"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypesinactive_v1(self, body: Any = None) -> Any:
        path = f"/processing/v1/jobtypes/inactive"
        return self._send("GET", path, body)

    def processing_jobs_getjobtypesinactive_v2(self, body: Any = None) -> Any:
        path = f"/processing/v2/jobtypes/inactive"
        return self._send("GET", path, body)

    def processing_jobs_updatefinish_v1(self, body: Optional[List[Processing_jobsUpdatefinishV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/finish"
        return self._send("PUT", path, body)

    def processing_jobs_updatefinish_v2(self, body: Optional[List[Processing_jobsUpdatefinishV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/finish"
        return self._send("PUT", path, body)

    def processing_jobs_updatejobtypes_v1(self, body: Optional[List[Processing_jobsUpdatejobtypesV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/jobtypes"
        return self._send("PUT", path, body)

    def processing_jobs_updatejobtypes_v2(self, body: Optional[List[Processing_jobsUpdatejobtypesV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/jobtypes"
        return self._send("PUT", path, body)

    def processing_jobs_updateunfinish_v1(self, body: Optional[List[Processing_jobsUpdateunfinishV1RequestItem]] = None) -> Any:
        path = f"/processing/v1/unfinish"
        return self._send("PUT", path, body)

    def processing_jobs_updateunfinish_v2(self, body: Optional[List[Processing_jobsUpdateunfinishV2RequestItem]] = None) -> Any:
        path = f"/processing/v2/unfinish"
        return self._send("PUT", path, body)

    def retail_id_createassociate_v2(self, body: Optional[List[Retail_idCreateassociateV2RequestItem]] = None) -> Any:
        path = f"/retailid/v2/associate"
        return self._send("POST", path, body)

    def retail_id_creategenerate_v2(self, body: Optional[Retail_idCreategenerateV2Request] = None) -> Any:
        path = f"/retailid/v2/generate"
        return self._send("POST", path, body)

    def retail_id_createmerge_v2(self, body: Optional[Retail_idCreatemergeV2Request] = None) -> Any:
        path = f"/retailid/v2/merge"
        return self._send("POST", path, body)

    def retail_id_createpackageinfo_v2(self, body: Optional[Retail_idCreatepackageinfoV2Request] = None) -> Any:
        path = f"/retailid/v2/packages/info"
        return self._send("POST", path, body)

    def retail_id_getreceivebylabel_v2(self, label: str, body: Any = None) -> Any:
        path = f"/retailid/v2/receive/{label}"
        return self._send("GET", path, body)

    def retail_id_getreceiveqrbyshortcode_v2(self, short_code: str, body: Any = None) -> Any:
        path = f"/retailid/v2/receive/qr/{short_code}"
        return self._send("GET", path, body)

    def sales_createdelivery_v1(self, body: Optional[List[SalesCreatedeliveryV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries"
        return self._send("POST", path, body)

    def sales_createdelivery_v2(self, body: Optional[List[SalesCreatedeliveryV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries"
        return self._send("POST", path, body)

    def sales_createdeliveryretailer_v1(self, body: Optional[List[SalesCreatedeliveryretailerV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/retailer"
        return self._send("POST", path, body)

    def sales_createdeliveryretailer_v2(self, body: Optional[List[SalesCreatedeliveryretailerV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/retailer"
        return self._send("POST", path, body)

    def sales_createdeliveryretailerdepart_v1(self, body: Optional[List[SalesCreatedeliveryretailerdepartV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/depart"
        return self._send("POST", path, body)

    def sales_createdeliveryretailerdepart_v2(self, body: Optional[List[SalesCreatedeliveryretailerdepartV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/depart"
        return self._send("POST", path, body)

    def sales_createdeliveryretailerend_v1(self, body: Optional[List[SalesCreatedeliveryretailerendV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/end"
        return self._send("POST", path, body)

    def sales_createdeliveryretailerend_v2(self, body: Optional[List[SalesCreatedeliveryretailerendV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/end"
        return self._send("POST", path, body)

    def sales_createdeliveryretailerrestock_v1(self, body: Optional[List[SalesCreatedeliveryretailerrestockV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/restock"
        return self._send("POST", path, body)

    def sales_createdeliveryretailerrestock_v2(self, body: Optional[List[SalesCreatedeliveryretailerrestockV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/restock"
        return self._send("POST", path, body)

    def sales_createdeliveryretailersale_v1(self, body: Optional[List[SalesCreatedeliveryretailersaleV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/sale"
        return self._send("POST", path, body)

    def sales_createdeliveryretailersale_v2(self, body: Optional[List[SalesCreatedeliveryretailersaleV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/sale"
        return self._send("POST", path, body)

    def sales_createreceipt_v1(self, body: Optional[List[SalesCreatereceiptV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/receipts"
        return self._send("POST", path, body)

    def sales_createreceipt_v2(self, body: Optional[List[SalesCreatereceiptV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/receipts"
        return self._send("POST", path, body)

    def sales_createtransactionbydate_v1(self, date: str, body: Optional[List[SalesCreatetransactionbydateV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/transactions/{date}"
        return self._send("POST", path, body)

    def sales_deletedelivery_v1(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/{id}"
        return self._send("DELETE", path, body)

    def sales_deletedelivery_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/{id}"
        return self._send("DELETE", path, body)

    def sales_deletedeliveryretailer_v1(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/{id}"
        return self._send("DELETE", path, body)

    def sales_deletedeliveryretailer_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/{id}"
        return self._send("DELETE", path, body)

    def sales_deletereceipt_v1(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v1/receipts/{id}"
        return self._send("DELETE", path, body)

    def sales_deletereceipt_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v2/receipts/{id}"
        return self._send("DELETE", path, body)

    def sales_getcounties_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/counties"
        return self._send("GET", path, body)

    def sales_getcounties_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/counties"
        return self._send("GET", path, body)

    def sales_getcustomertypes_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/customertypes"
        return self._send("GET", path, body)

    def sales_getcustomertypes_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/customertypes"
        return self._send("GET", path, body)

    def sales_getdeliveriesactive_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/active"
        return self._send("GET", path, body)

    def sales_getdeliveriesactive_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/active"
        return self._send("GET", path, body)

    def sales_getdeliveriesinactive_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/inactive"
        return self._send("GET", path, body)

    def sales_getdeliveriesinactive_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/inactive"
        return self._send("GET", path, body)

    def sales_getdeliveriesretaileractive_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/active"
        return self._send("GET", path, body)

    def sales_getdeliveriesretaileractive_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/active"
        return self._send("GET", path, body)

    def sales_getdeliveriesretailerinactive_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/inactive"
        return self._send("GET", path, body)

    def sales_getdeliveriesretailerinactive_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/inactive"
        return self._send("GET", path, body)

    def sales_getdeliveriesreturnreasons_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/returnreasons"
        return self._send("GET", path, body)

    def sales_getdeliveriesreturnreasons_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/returnreasons"
        return self._send("GET", path, body)

    def sales_getdelivery_v1(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/{id}"
        return self._send("GET", path, body)

    def sales_getdelivery_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/{id}"
        return self._send("GET", path, body)

    def sales_getdeliveryretailer_v1(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v1/deliveries/retailer/{id}"
        return self._send("GET", path, body)

    def sales_getdeliveryretailer_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v2/deliveries/retailer/{id}"
        return self._send("GET", path, body)

    def sales_getpatientregistrationslocations_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/patientregistration/locations"
        return self._send("GET", path, body)

    def sales_getpatientregistrationslocations_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/patientregistration/locations"
        return self._send("GET", path, body)

    def sales_getpaymenttypes_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/paymenttypes"
        return self._send("GET", path, body)

    def sales_getpaymenttypes_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/paymenttypes"
        return self._send("GET", path, body)

    def sales_getreceipt_v1(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v1/receipts/{id}"
        return self._send("GET", path, body)

    def sales_getreceipt_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sales/v2/receipts/{id}"
        return self._send("GET", path, body)

    def sales_getreceiptsactive_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/receipts/active"
        return self._send("GET", path, body)

    def sales_getreceiptsactive_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/receipts/active"
        return self._send("GET", path, body)

    def sales_getreceiptsexternalbyexternalnumber_v2(self, external_number: str, body: Any = None) -> Any:
        path = f"/sales/v2/receipts/external/{external_number}"
        return self._send("GET", path, body)

    def sales_getreceiptsinactive_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/receipts/inactive"
        return self._send("GET", path, body)

    def sales_getreceiptsinactive_v2(self, body: Any = None) -> Any:
        path = f"/sales/v2/receipts/inactive"
        return self._send("GET", path, body)

    def sales_gettransactions_v1(self, body: Any = None) -> Any:
        path = f"/sales/v1/transactions"
        return self._send("GET", path, body)

    def sales_gettransactionsbysalesdatestartandsalesdateend_v1(self, sales_date_start: str, sales_date_end: str, body: Any = None) -> Any:
        path = f"/sales/v1/transactions/{sales_date_start}/{sales_date_end}"
        return self._send("GET", path, body)

    def sales_updatedelivery_v1(self, body: Optional[List[SalesUpdatedeliveryV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries"
        return self._send("PUT", path, body)

    def sales_updatedelivery_v2(self, body: Optional[List[SalesUpdatedeliveryV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries"
        return self._send("PUT", path, body)

    def sales_updatedeliverycomplete_v1(self, body: Optional[List[SalesUpdatedeliverycompleteV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/complete"
        return self._send("PUT", path, body)

    def sales_updatedeliverycomplete_v2(self, body: Optional[List[SalesUpdatedeliverycompleteV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/complete"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhub_v1(self, body: Optional[List[SalesUpdatedeliveryhubV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/hub"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhub_v2(self, body: Optional[List[SalesUpdatedeliveryhubV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/hub"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhubaccept_v1(self, body: Optional[List[SalesUpdatedeliveryhubacceptV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/hub/accept"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhubaccept_v2(self, body: Optional[List[SalesUpdatedeliveryhubacceptV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/hub/accept"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhubdepart_v1(self, body: Optional[List[SalesUpdatedeliveryhubdepartV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/hub/depart"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhubdepart_v2(self, body: Optional[List[SalesUpdatedeliveryhubdepartV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/hub/depart"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhubverifyid_v1(self, body: Optional[List[SalesUpdatedeliveryhubverifyidV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/hub/verifyID"
        return self._send("PUT", path, body)

    def sales_updatedeliveryhubverifyid_v2(self, body: Optional[List[SalesUpdatedeliveryhubverifyidV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/hub/verifyID"
        return self._send("PUT", path, body)

    def sales_updatedeliveryretailer_v1(self, body: Optional[List[SalesUpdatedeliveryretailerV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/deliveries/retailer"
        return self._send("PUT", path, body)

    def sales_updatedeliveryretailer_v2(self, body: Optional[List[SalesUpdatedeliveryretailerV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/deliveries/retailer"
        return self._send("PUT", path, body)

    def sales_updatereceipt_v1(self, body: Optional[List[SalesUpdatereceiptV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/receipts"
        return self._send("PUT", path, body)

    def sales_updatereceipt_v2(self, body: Optional[List[SalesUpdatereceiptV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/receipts"
        return self._send("PUT", path, body)

    def sales_updatereceiptfinalize_v2(self, body: Optional[List[SalesUpdatereceiptfinalizeV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/receipts/finalize"
        return self._send("PUT", path, body)

    def sales_updatereceiptunfinalize_v2(self, body: Optional[List[SalesUpdatereceiptunfinalizeV2RequestItem]] = None) -> Any:
        path = f"/sales/v2/receipts/unfinalize"
        return self._send("PUT", path, body)

    def sales_updatetransactionbydate_v1(self, date: str, body: Optional[List[SalesUpdatetransactionbydateV1RequestItem]] = None) -> Any:
        path = f"/sales/v1/transactions/{date}"
        return self._send("PUT", path, body)

    def tags_getpackageavailable_v2(self, body: Any = None) -> Any:
        path = f"/tags/v2/package/available"
        return self._send("GET", path, body)

    def tags_getplantavailable_v2(self, body: Any = None) -> Any:
        path = f"/tags/v2/plant/available"
        return self._send("GET", path, body)

    def tags_getstaged_v2(self, body: Any = None) -> Any:
        path = f"/tags/v2/staged"
        return self._send("GET", path, body)

    def caregivers_status_getbycaregiverlicensenumber_v1(self, caregiver_license_number: str, body: Any = None) -> Any:
        path = f"/caregivers/v1/status/{caregiver_license_number}"
        return self._send("GET", path, body)

    def caregivers_status_getbycaregiverlicensenumber_v2(self, caregiver_license_number: str, body: Any = None) -> Any:
        path = f"/caregivers/v2/status/{caregiver_license_number}"
        return self._send("GET", path, body)

    def employees_getall_v1(self, body: Any = None) -> Any:
        path = f"/employees/v1"
        return self._send("GET", path, body)

    def employees_getall_v2(self, body: Any = None) -> Any:
        path = f"/employees/v2"
        return self._send("GET", path, body)

    def employees_getpermissions_v2(self, body: Any = None) -> Any:
        path = f"/employees/v2/permissions"
        return self._send("GET", path, body)

    def patient_check_ins_create_v1(self, body: Optional[List[Patient_check_insCreateV1RequestItem]] = None) -> Any:
        path = f"/patient-checkins/v1"
        return self._send("POST", path, body)

    def patient_check_ins_create_v2(self, body: Optional[List[Patient_check_insCreateV2RequestItem]] = None) -> Any:
        path = f"/patient-checkins/v2"
        return self._send("POST", path, body)

    def patient_check_ins_delete_v1(self, id: str, body: Any = None) -> Any:
        path = f"/patient-checkins/v1/{id}"
        return self._send("DELETE", path, body)

    def patient_check_ins_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/patient-checkins/v2/{id}"
        return self._send("DELETE", path, body)

    def patient_check_ins_getall_v1(self, body: Any = None) -> Any:
        path = f"/patient-checkins/v1"
        return self._send("GET", path, body)

    def patient_check_ins_getall_v2(self, body: Any = None) -> Any:
        path = f"/patient-checkins/v2"
        return self._send("GET", path, body)

    def patient_check_ins_getlocations_v1(self, body: Any = None) -> Any:
        path = f"/patient-checkins/v1/locations"
        return self._send("GET", path, body)

    def patient_check_ins_getlocations_v2(self, body: Any = None) -> Any:
        path = f"/patient-checkins/v2/locations"
        return self._send("GET", path, body)

    def patient_check_ins_update_v1(self, body: Optional[List[Patient_check_insUpdateV1RequestItem]] = None) -> Any:
        path = f"/patient-checkins/v1"
        return self._send("PUT", path, body)

    def patient_check_ins_update_v2(self, body: Optional[List[Patient_check_insUpdateV2RequestItem]] = None) -> Any:
        path = f"/patient-checkins/v2"
        return self._send("PUT", path, body)

    def plant_batches_createadditives_v1(self, body: Optional[List[Plant_batchesCreateadditivesV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/additives"
        return self._send("POST", path, body)

    def plant_batches_createadditives_v2(self, body: Optional[List[Plant_batchesCreateadditivesV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/additives"
        return self._send("POST", path, body)

    def plant_batches_createadditivesusingtemplate_v2(self, body: Optional[List[Plant_batchesCreateadditivesusingtemplateV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/additives/usingtemplate"
        return self._send("POST", path, body)

    def plant_batches_createadjust_v1(self, body: Optional[List[Plant_batchesCreateadjustV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/adjust"
        return self._send("POST", path, body)

    def plant_batches_createadjust_v2(self, body: Optional[List[Plant_batchesCreateadjustV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/adjust"
        return self._send("POST", path, body)

    def plant_batches_createchangegrowthphase_v1(self, body: Optional[List[Plant_batchesCreatechangegrowthphaseV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/changegrowthphase"
        return self._send("POST", path, body)

    def plant_batches_creategrowthphase_v2(self, body: Optional[List[Plant_batchesCreategrowthphaseV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/growthphase"
        return self._send("POST", path, body)

    def plant_batches_createpackage_v2(self, body: Optional[List[Plant_batchesCreatepackageV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/packages"
        return self._send("POST", path, body)

    def plant_batches_createpackagefrommotherplant_v1(self, body: Optional[List[Plant_batchesCreatepackagefrommotherplantV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/create/packages/frommotherplant"
        return self._send("POST", path, body)

    def plant_batches_createpackagefrommotherplant_v2(self, body: Optional[List[Plant_batchesCreatepackagefrommotherplantV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/packages/frommotherplant"
        return self._send("POST", path, body)

    def plant_batches_createplantings_v2(self, body: Optional[List[Plant_batchesCreateplantingsV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/plantings"
        return self._send("POST", path, body)

    def plant_batches_createsplit_v1(self, body: Optional[List[Plant_batchesCreatesplitV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/split"
        return self._send("POST", path, body)

    def plant_batches_createsplit_v2(self, body: Optional[List[Plant_batchesCreatesplitV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/split"
        return self._send("POST", path, body)

    def plant_batches_createwaste_v1(self, body: Optional[List[Plant_batchesCreatewasteV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/waste"
        return self._send("POST", path, body)

    def plant_batches_createwaste_v2(self, body: Optional[List[Plant_batchesCreatewasteV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/waste"
        return self._send("POST", path, body)

    def plant_batches_createpackages_v1(self, body: Optional[List[Plant_batchesCreatepackagesV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/createpackages"
        return self._send("POST", path, body)

    def plant_batches_createplantings_v1(self, body: Optional[List[Plant_batchesCreateplantingsV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/createplantings"
        return self._send("POST", path, body)

    def plant_batches_delete_v1(self, body: Any = None) -> Any:
        path = f"/plantbatches/v1"
        return self._send("DELETE", path, body)

    def plant_batches_delete_v2(self, body: Any = None) -> Any:
        path = f"/plantbatches/v2"
        return self._send("DELETE", path, body)

    def plant_batches_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/plantbatches/v1/{id}"
        return self._send("GET", path, body)

    def plant_batches_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/plantbatches/v2/{id}"
        return self._send("GET", path, body)

    def plant_batches_getactive_v1(self, body: Any = None) -> Any:
        path = f"/plantbatches/v1/active"
        return self._send("GET", path, body)

    def plant_batches_getactive_v2(self, body: Any = None) -> Any:
        path = f"/plantbatches/v2/active"
        return self._send("GET", path, body)

    def plant_batches_getinactive_v1(self, body: Any = None) -> Any:
        path = f"/plantbatches/v1/inactive"
        return self._send("GET", path, body)

    def plant_batches_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/plantbatches/v2/inactive"
        return self._send("GET", path, body)

    def plant_batches_gettypes_v1(self, body: Any = None) -> Any:
        path = f"/plantbatches/v1/types"
        return self._send("GET", path, body)

    def plant_batches_gettypes_v2(self, body: Any = None) -> Any:
        path = f"/plantbatches/v2/types"
        return self._send("GET", path, body)

    def plant_batches_getwaste_v2(self, body: Any = None) -> Any:
        path = f"/plantbatches/v2/waste"
        return self._send("GET", path, body)

    def plant_batches_getwastereasons_v1(self, body: Any = None) -> Any:
        path = f"/plantbatches/v1/waste/reasons"
        return self._send("GET", path, body)

    def plant_batches_getwastereasons_v2(self, body: Any = None) -> Any:
        path = f"/plantbatches/v2/waste/reasons"
        return self._send("GET", path, body)

    def plant_batches_updatelocation_v2(self, body: Optional[List[Plant_batchesUpdatelocationV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/location"
        return self._send("PUT", path, body)

    def plant_batches_updatemoveplantbatches_v1(self, body: Optional[List[Plant_batchesUpdatemoveplantbatchesV1RequestItem]] = None) -> Any:
        path = f"/plantbatches/v1/moveplantbatches"
        return self._send("PUT", path, body)

    def plant_batches_updatename_v2(self, body: Optional[List[Plant_batchesUpdatenameV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/name"
        return self._send("PUT", path, body)

    def plant_batches_updatestrain_v2(self, body: Optional[List[Plant_batchesUpdatestrainV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/strain"
        return self._send("PUT", path, body)

    def plant_batches_updatetag_v2(self, body: Optional[List[Plant_batchesUpdatetagV2RequestItem]] = None) -> Any:
        path = f"/plantbatches/v2/tag"
        return self._send("PUT", path, body)

    def plants_createadditives_v1(self, body: Optional[List[PlantsCreateadditivesV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/additives"
        return self._send("POST", path, body)

    def plants_createadditives_v2(self, body: Optional[List[PlantsCreateadditivesV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/additives"
        return self._send("POST", path, body)

    def plants_createadditivesbylocation_v1(self, body: Optional[List[PlantsCreateadditivesbylocationV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/additives/bylocation"
        return self._send("POST", path, body)

    def plants_createadditivesbylocation_v2(self, body: Optional[List[PlantsCreateadditivesbylocationV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/additives/bylocation"
        return self._send("POST", path, body)

    def plants_createadditivesbylocationusingtemplate_v2(self, body: Optional[List[PlantsCreateadditivesbylocationusingtemplateV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/additives/bylocation/usingtemplate"
        return self._send("POST", path, body)

    def plants_createadditivesusingtemplate_v2(self, body: Optional[List[PlantsCreateadditivesusingtemplateV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/additives/usingtemplate"
        return self._send("POST", path, body)

    def plants_createchangegrowthphases_v1(self, body: Optional[List[PlantsCreatechangegrowthphasesV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/changegrowthphases"
        return self._send("POST", path, body)

    def plants_createharvestplants_v1(self, body: Optional[List[PlantsCreateharvestplantsV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/harvestplants"
        return self._send("POST", path, body)

    def plants_createmanicure_v2(self, body: Optional[List[PlantsCreatemanicureV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/manicure"
        return self._send("POST", path, body)

    def plants_createmanicureplants_v1(self, body: Optional[List[PlantsCreatemanicureplantsV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/manicureplants"
        return self._send("POST", path, body)

    def plants_createmoveplants_v1(self, body: Optional[List[PlantsCreatemoveplantsV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/moveplants"
        return self._send("POST", path, body)

    def plants_createplantbatchpackage_v1(self, body: Optional[List[PlantsCreateplantbatchpackageV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/create/plantbatch/packages"
        return self._send("POST", path, body)

    def plants_createplantbatchpackage_v2(self, body: Optional[List[PlantsCreateplantbatchpackageV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/plantbatch/packages"
        return self._send("POST", path, body)

    def plants_createplantings_v1(self, body: Optional[List[PlantsCreateplantingsV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/create/plantings"
        return self._send("POST", path, body)

    def plants_createplantings_v2(self, body: Optional[List[PlantsCreateplantingsV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/plantings"
        return self._send("POST", path, body)

    def plants_createwaste_v1(self, body: Optional[List[PlantsCreatewasteV1RequestItem]] = None) -> Any:
        path = f"/plants/v1/waste"
        return self._send("POST", path, body)

    def plants_createwaste_v2(self, body: Optional[List[PlantsCreatewasteV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/waste"
        return self._send("POST", path, body)

    def plants_delete_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1"
        return self._send("DELETE", path, body)

    def plants_delete_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2"
        return self._send("DELETE", path, body)

    def plants_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/plants/v1/{id}"
        return self._send("GET", path, body)

    def plants_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/plants/v2/{id}"
        return self._send("GET", path, body)

    def plants_getadditives_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/additives"
        return self._send("GET", path, body)

    def plants_getadditives_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/additives"
        return self._send("GET", path, body)

    def plants_getadditivestypes_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/additives/types"
        return self._send("GET", path, body)

    def plants_getadditivestypes_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/additives/types"
        return self._send("GET", path, body)

    def plants_getbylabel_v1(self, label: str, body: Any = None) -> Any:
        path = f"/plants/v1/{label}"
        return self._send("GET", path, body)

    def plants_getbylabel_v2(self, label: str, body: Any = None) -> Any:
        path = f"/plants/v2/{label}"
        return self._send("GET", path, body)

    def plants_getflowering_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/flowering"
        return self._send("GET", path, body)

    def plants_getflowering_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/flowering"
        return self._send("GET", path, body)

    def plants_getgrowthphases_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/growthphases"
        return self._send("GET", path, body)

    def plants_getgrowthphases_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/growthphases"
        return self._send("GET", path, body)

    def plants_getinactive_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/inactive"
        return self._send("GET", path, body)

    def plants_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/inactive"
        return self._send("GET", path, body)

    def plants_getmother_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/mother"
        return self._send("GET", path, body)

    def plants_getmotherinactive_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/mother/inactive"
        return self._send("GET", path, body)

    def plants_getmotheronhold_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/mother/onhold"
        return self._send("GET", path, body)

    def plants_getonhold_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/onhold"
        return self._send("GET", path, body)

    def plants_getonhold_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/onhold"
        return self._send("GET", path, body)

    def plants_getvegetative_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/vegetative"
        return self._send("GET", path, body)

    def plants_getvegetative_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/vegetative"
        return self._send("GET", path, body)

    def plants_getwaste_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/waste"
        return self._send("GET", path, body)

    def plants_getwastemethodsall_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/waste/methods/all"
        return self._send("GET", path, body)

    def plants_getwastemethodsall_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/waste/methods/all"
        return self._send("GET", path, body)

    def plants_getwastepackage_v2(self, id: str, body: Any = None) -> Any:
        path = f"/plants/v2/waste/{id}/package"
        return self._send("GET", path, body)

    def plants_getwasteplant_v2(self, id: str, body: Any = None) -> Any:
        path = f"/plants/v2/waste/{id}/plant"
        return self._send("GET", path, body)

    def plants_getwastereasons_v1(self, body: Any = None) -> Any:
        path = f"/plants/v1/waste/reasons"
        return self._send("GET", path, body)

    def plants_getwastereasons_v2(self, body: Any = None) -> Any:
        path = f"/plants/v2/waste/reasons"
        return self._send("GET", path, body)

    def plants_updateadjust_v2(self, body: Optional[List[PlantsUpdateadjustV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/adjust"
        return self._send("PUT", path, body)

    def plants_updategrowthphase_v2(self, body: Optional[List[PlantsUpdategrowthphaseV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/growthphase"
        return self._send("PUT", path, body)

    def plants_updateharvest_v2(self, body: Optional[List[PlantsUpdateharvestV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/harvest"
        return self._send("PUT", path, body)

    def plants_updatelocation_v2(self, body: Optional[List[PlantsUpdatelocationV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/location"
        return self._send("PUT", path, body)

    def plants_updatemerge_v2(self, body: Optional[List[PlantsUpdatemergeV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/merge"
        return self._send("PUT", path, body)

    def plants_updatesplit_v2(self, body: Optional[List[PlantsUpdatesplitV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/split"
        return self._send("PUT", path, body)

    def plants_updatestrain_v2(self, body: Optional[List[PlantsUpdatestrainV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/strain"
        return self._send("PUT", path, body)

    def plants_updatetag_v2(self, body: Optional[List[PlantsUpdatetagV2RequestItem]] = None) -> Any:
        path = f"/plants/v2/tag"
        return self._send("PUT", path, body)

    def sublocations_create_v2(self, body: Optional[List[SublocationsCreateV2RequestItem]] = None) -> Any:
        path = f"/sublocations/v2"
        return self._send("POST", path, body)

    def sublocations_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sublocations/v2/{id}"
        return self._send("DELETE", path, body)

    def sublocations_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/sublocations/v2/{id}"
        return self._send("GET", path, body)

    def sublocations_getactive_v2(self, body: Any = None) -> Any:
        path = f"/sublocations/v2/active"
        return self._send("GET", path, body)

    def sublocations_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/sublocations/v2/inactive"
        return self._send("GET", path, body)

    def sublocations_update_v2(self, body: Optional[List[SublocationsUpdateV2RequestItem]] = None) -> Any:
        path = f"/sublocations/v2"
        return self._send("PUT", path, body)

    def units_of_measure_getactive_v1(self, body: Any = None) -> Any:
        path = f"/unitsofmeasure/v1/active"
        return self._send("GET", path, body)

    def units_of_measure_getactive_v2(self, body: Any = None) -> Any:
        path = f"/unitsofmeasure/v2/active"
        return self._send("GET", path, body)

    def units_of_measure_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/unitsofmeasure/v2/inactive"
        return self._send("GET", path, body)

    def additives_templates_create_v2(self, body: Optional[List[Additives_templatesCreateV2RequestItem]] = None) -> Any:
        path = f"/additivestemplates/v2"
        return self._send("POST", path, body)

    def additives_templates_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/additivestemplates/v2/{id}"
        return self._send("GET", path, body)

    def additives_templates_getactive_v2(self, body: Any = None) -> Any:
        path = f"/additivestemplates/v2/active"
        return self._send("GET", path, body)

    def additives_templates_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/additivestemplates/v2/inactive"
        return self._send("GET", path, body)

    def additives_templates_update_v2(self, body: Optional[List[Additives_templatesUpdateV2RequestItem]] = None) -> Any:
        path = f"/additivestemplates/v2"
        return self._send("PUT", path, body)

    def patients_status_getstatusesbypatientlicensenumber_v1(self, patient_license_number: str, body: Any = None) -> Any:
        path = f"/patients/v1/statuses/{patient_license_number}"
        return self._send("GET", path, body)

    def patients_status_getstatusesbypatientlicensenumber_v2(self, patient_license_number: str, body: Any = None) -> Any:
        path = f"/patients/v2/statuses/{patient_license_number}"
        return self._send("GET", path, body)

    def strains_create_v1(self, body: Optional[List[StrainsCreateV1RequestItem]] = None) -> Any:
        path = f"/strains/v1/create"
        return self._send("POST", path, body)

    def strains_create_v2(self, body: Optional[List[StrainsCreateV2RequestItem]] = None) -> Any:
        path = f"/strains/v2"
        return self._send("POST", path, body)

    def strains_createupdate_v1(self, body: Optional[List[StrainsCreateupdateV1RequestItem]] = None) -> Any:
        path = f"/strains/v1/update"
        return self._send("POST", path, body)

    def strains_delete_v1(self, id: str, body: Any = None) -> Any:
        path = f"/strains/v1/{id}"
        return self._send("DELETE", path, body)

    def strains_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/strains/v2/{id}"
        return self._send("DELETE", path, body)

    def strains_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/strains/v1/{id}"
        return self._send("GET", path, body)

    def strains_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/strains/v2/{id}"
        return self._send("GET", path, body)

    def strains_getactive_v1(self, body: Any = None) -> Any:
        path = f"/strains/v1/active"
        return self._send("GET", path, body)

    def strains_getactive_v2(self, body: Any = None) -> Any:
        path = f"/strains/v2/active"
        return self._send("GET", path, body)

    def strains_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/strains/v2/inactive"
        return self._send("GET", path, body)

    def strains_update_v2(self, body: Optional[List[StrainsUpdateV2RequestItem]] = None) -> Any:
        path = f"/strains/v2"
        return self._send("PUT", path, body)

    def transfers_createexternalincoming_v1(self, body: Optional[List[TransfersCreateexternalincomingV1RequestItem]] = None) -> Any:
        path = f"/transfers/v1/external/incoming"
        return self._send("POST", path, body)

    def transfers_createexternalincoming_v2(self, body: Optional[List[TransfersCreateexternalincomingV2RequestItem]] = None) -> Any:
        path = f"/transfers/v2/external/incoming"
        return self._send("POST", path, body)

    def transfers_createtemplates_v1(self, body: Optional[List[TransfersCreatetemplatesV1RequestItem]] = None) -> Any:
        path = f"/transfers/v1/templates"
        return self._send("POST", path, body)

    def transfers_createtemplatesoutgoing_v2(self, body: Optional[List[TransfersCreatetemplatesoutgoingV2RequestItem]] = None) -> Any:
        path = f"/transfers/v2/templates/outgoing"
        return self._send("POST", path, body)

    def transfers_deleteexternalincoming_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/external/incoming/{id}"
        return self._send("DELETE", path, body)

    def transfers_deleteexternalincoming_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/external/incoming/{id}"
        return self._send("DELETE", path, body)

    def transfers_deletetemplates_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/templates/{id}"
        return self._send("DELETE", path, body)

    def transfers_deletetemplatesoutgoing_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/templates/outgoing/{id}"
        return self._send("DELETE", path, body)

    def transfers_getdeliveriespackagesstates_v1(self, body: Any = None) -> Any:
        path = f"/transfers/v1/deliveries/packages/states"
        return self._send("GET", path, body)

    def transfers_getdeliveriespackagesstates_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/deliveries/packages/states"
        return self._send("GET", path, body)

    def transfers_getdelivery_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/{id}/deliveries"
        return self._send("GET", path, body)

    def transfers_getdelivery_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/{id}/deliveries"
        return self._send("GET", path, body)

    def transfers_getdeliverypackage_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/deliveries/{id}/packages"
        return self._send("GET", path, body)

    def transfers_getdeliverypackage_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/deliveries/{id}/packages"
        return self._send("GET", path, body)

    def transfers_getdeliverypackagerequiredlabtestbatches_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/deliveries/package/{id}/requiredlabtestbatches"
        return self._send("GET", path, body)

    def transfers_getdeliverypackagerequiredlabtestbatches_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/deliveries/package/{id}/requiredlabtestbatches"
        return self._send("GET", path, body)

    def transfers_getdeliverypackagewholesale_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/deliveries/{id}/packages/wholesale"
        return self._send("GET", path, body)

    def transfers_getdeliverypackagewholesale_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/deliveries/{id}/packages/wholesale"
        return self._send("GET", path, body)

    def transfers_getdeliverytransporters_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/deliveries/{id}/transporters"
        return self._send("GET", path, body)

    def transfers_getdeliverytransporters_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/deliveries/{id}/transporters"
        return self._send("GET", path, body)

    def transfers_getdeliverytransportersdetails_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/deliveries/{id}/transporters/details"
        return self._send("GET", path, body)

    def transfers_getdeliverytransportersdetails_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/deliveries/{id}/transporters/details"
        return self._send("GET", path, body)

    def transfers_gethub_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/hub"
        return self._send("GET", path, body)

    def transfers_getincoming_v1(self, body: Any = None) -> Any:
        path = f"/transfers/v1/incoming"
        return self._send("GET", path, body)

    def transfers_getincoming_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/incoming"
        return self._send("GET", path, body)

    def transfers_getoutgoing_v1(self, body: Any = None) -> Any:
        path = f"/transfers/v1/outgoing"
        return self._send("GET", path, body)

    def transfers_getoutgoing_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/outgoing"
        return self._send("GET", path, body)

    def transfers_getrejected_v1(self, body: Any = None) -> Any:
        path = f"/transfers/v1/rejected"
        return self._send("GET", path, body)

    def transfers_getrejected_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/rejected"
        return self._send("GET", path, body)

    def transfers_gettemplates_v1(self, body: Any = None) -> Any:
        path = f"/transfers/v1/templates"
        return self._send("GET", path, body)

    def transfers_gettemplatesdelivery_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/templates/{id}/deliveries"
        return self._send("GET", path, body)

    def transfers_gettemplatesdeliverypackage_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/templates/deliveries/{id}/packages"
        return self._send("GET", path, body)

    def transfers_gettemplatesdeliverytransporters_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/templates/deliveries/{id}/transporters"
        return self._send("GET", path, body)

    def transfers_gettemplatesdeliverytransportersdetails_v1(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v1/templates/deliveries/{id}/transporters/details"
        return self._send("GET", path, body)

    def transfers_gettemplatesoutgoing_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/templates/outgoing"
        return self._send("GET", path, body)

    def transfers_gettemplatesoutgoingdelivery_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/templates/outgoing/{id}/deliveries"
        return self._send("GET", path, body)

    def transfers_gettemplatesoutgoingdeliverypackage_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/templates/outgoing/deliveries/{id}/packages"
        return self._send("GET", path, body)

    def transfers_gettemplatesoutgoingdeliverytransporters_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/templates/outgoing/deliveries/{id}/transporters"
        return self._send("GET", path, body)

    def transfers_gettemplatesoutgoingdeliverytransportersdetails_v2(self, id: str, body: Any = None) -> Any:
        path = f"/transfers/v2/templates/outgoing/deliveries/{id}/transporters/details"
        return self._send("GET", path, body)

    def transfers_gettypes_v1(self, body: Any = None) -> Any:
        path = f"/transfers/v1/types"
        return self._send("GET", path, body)

    def transfers_gettypes_v2(self, body: Any = None) -> Any:
        path = f"/transfers/v2/types"
        return self._send("GET", path, body)

    def transfers_updateexternalincoming_v1(self, body: Optional[List[TransfersUpdateexternalincomingV1RequestItem]] = None) -> Any:
        path = f"/transfers/v1/external/incoming"
        return self._send("PUT", path, body)

    def transfers_updateexternalincoming_v2(self, body: Optional[List[TransfersUpdateexternalincomingV2RequestItem]] = None) -> Any:
        path = f"/transfers/v2/external/incoming"
        return self._send("PUT", path, body)

    def transfers_updatetemplates_v1(self, body: Optional[List[TransfersUpdatetemplatesV1RequestItem]] = None) -> Any:
        path = f"/transfers/v1/templates"
        return self._send("PUT", path, body)

    def transfers_updatetemplatesoutgoing_v2(self, body: Optional[List[TransfersUpdatetemplatesoutgoingV2RequestItem]] = None) -> Any:
        path = f"/transfers/v2/templates/outgoing"
        return self._send("PUT", path, body)

    def waste_methods_getall_v2(self, body: Any = None) -> Any:
        path = f"/wastemethods/v2"
        return self._send("GET", path, body)

    def facilities_getall_v1(self, body: Any = None) -> Any:
        path = f"/facilities/v1"
        return self._send("GET", path, body)

    def facilities_getall_v2(self, body: Any = None) -> Any:
        path = f"/facilities/v2"
        return self._send("GET", path, body)

    def harvests_createfinish_v1(self, body: Optional[List[HarvestsCreatefinishV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/finish"
        return self._send("POST", path, body)

    def harvests_createpackage_v1(self, body: Optional[List[HarvestsCreatepackageV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/create/packages"
        return self._send("POST", path, body)

    def harvests_createpackage_v2(self, body: Optional[List[HarvestsCreatepackageV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/packages"
        return self._send("POST", path, body)

    def harvests_createpackagetesting_v1(self, body: Optional[List[HarvestsCreatepackagetestingV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/create/packages/testing"
        return self._send("POST", path, body)

    def harvests_createpackagetesting_v2(self, body: Optional[List[HarvestsCreatepackagetestingV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/packages/testing"
        return self._send("POST", path, body)

    def harvests_createremovewaste_v1(self, body: Optional[List[HarvestsCreateremovewasteV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/removewaste"
        return self._send("POST", path, body)

    def harvests_createunfinish_v1(self, body: Optional[List[HarvestsCreateunfinishV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/unfinish"
        return self._send("POST", path, body)

    def harvests_createwaste_v2(self, body: Optional[List[HarvestsCreatewasteV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/waste"
        return self._send("POST", path, body)

    def harvests_deletewaste_v2(self, id: str, body: Any = None) -> Any:
        path = f"/harvests/v2/waste/{id}"
        return self._send("DELETE", path, body)

    def harvests_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/harvests/v1/{id}"
        return self._send("GET", path, body)

    def harvests_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/harvests/v2/{id}"
        return self._send("GET", path, body)

    def harvests_getactive_v1(self, body: Any = None) -> Any:
        path = f"/harvests/v1/active"
        return self._send("GET", path, body)

    def harvests_getactive_v2(self, body: Any = None) -> Any:
        path = f"/harvests/v2/active"
        return self._send("GET", path, body)

    def harvests_getinactive_v1(self, body: Any = None) -> Any:
        path = f"/harvests/v1/inactive"
        return self._send("GET", path, body)

    def harvests_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/harvests/v2/inactive"
        return self._send("GET", path, body)

    def harvests_getonhold_v1(self, body: Any = None) -> Any:
        path = f"/harvests/v1/onhold"
        return self._send("GET", path, body)

    def harvests_getonhold_v2(self, body: Any = None) -> Any:
        path = f"/harvests/v2/onhold"
        return self._send("GET", path, body)

    def harvests_getwaste_v2(self, body: Any = None) -> Any:
        path = f"/harvests/v2/waste"
        return self._send("GET", path, body)

    def harvests_getwastetypes_v1(self, body: Any = None) -> Any:
        path = f"/harvests/v1/waste/types"
        return self._send("GET", path, body)

    def harvests_getwastetypes_v2(self, body: Any = None) -> Any:
        path = f"/harvests/v2/waste/types"
        return self._send("GET", path, body)

    def harvests_updatefinish_v2(self, body: Optional[List[HarvestsUpdatefinishV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/finish"
        return self._send("PUT", path, body)

    def harvests_updatelocation_v2(self, body: Optional[List[HarvestsUpdatelocationV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/location"
        return self._send("PUT", path, body)

    def harvests_updatemove_v1(self, body: Optional[List[HarvestsUpdatemoveV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/move"
        return self._send("PUT", path, body)

    def harvests_updaterename_v1(self, body: Optional[List[HarvestsUpdaterenameV1RequestItem]] = None) -> Any:
        path = f"/harvests/v1/rename"
        return self._send("PUT", path, body)

    def harvests_updaterename_v2(self, body: Optional[List[HarvestsUpdaterenameV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/rename"
        return self._send("PUT", path, body)

    def harvests_updaterestoreharvestedplants_v2(self, body: Optional[List[HarvestsUpdaterestoreharvestedplantsV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/restore/harvestedplants"
        return self._send("PUT", path, body)

    def harvests_updateunfinish_v2(self, body: Optional[List[HarvestsUpdateunfinishV2RequestItem]] = None) -> Any:
        path = f"/harvests/v2/unfinish"
        return self._send("PUT", path, body)

    def items_create_v1(self, body: Optional[List[ItemsCreateV1RequestItem]] = None) -> Any:
        path = f"/items/v1/create"
        return self._send("POST", path, body)

    def items_create_v2(self, body: Optional[List[ItemsCreateV2RequestItem]] = None) -> Any:
        path = f"/items/v2"
        return self._send("POST", path, body)

    def items_createbrand_v2(self, body: Optional[List[ItemsCreatebrandV2RequestItem]] = None) -> Any:
        path = f"/items/v2/brand"
        return self._send("POST", path, body)

    def items_createfile_v2(self, body: Optional[List[ItemsCreatefileV2RequestItem]] = None) -> Any:
        path = f"/items/v2/file"
        return self._send("POST", path, body)

    def items_createphoto_v1(self, body: Optional[List[ItemsCreatephotoV1RequestItem]] = None) -> Any:
        path = f"/items/v1/photo"
        return self._send("POST", path, body)

    def items_createphoto_v2(self, body: Optional[List[ItemsCreatephotoV2RequestItem]] = None) -> Any:
        path = f"/items/v2/photo"
        return self._send("POST", path, body)

    def items_createupdate_v1(self, body: Optional[List[ItemsCreateupdateV1RequestItem]] = None) -> Any:
        path = f"/items/v1/update"
        return self._send("POST", path, body)

    def items_delete_v1(self, id: str, body: Any = None) -> Any:
        path = f"/items/v1/{id}"
        return self._send("DELETE", path, body)

    def items_delete_v2(self, id: str, body: Any = None) -> Any:
        path = f"/items/v2/{id}"
        return self._send("DELETE", path, body)

    def items_deletebrand_v2(self, id: str, body: Any = None) -> Any:
        path = f"/items/v2/brand/{id}"
        return self._send("DELETE", path, body)

    def items_get_v1(self, id: str, body: Any = None) -> Any:
        path = f"/items/v1/{id}"
        return self._send("GET", path, body)

    def items_get_v2(self, id: str, body: Any = None) -> Any:
        path = f"/items/v2/{id}"
        return self._send("GET", path, body)

    def items_getactive_v1(self, body: Any = None) -> Any:
        path = f"/items/v1/active"
        return self._send("GET", path, body)

    def items_getactive_v2(self, body: Any = None) -> Any:
        path = f"/items/v2/active"
        return self._send("GET", path, body)

    def items_getbrands_v1(self, body: Any = None) -> Any:
        path = f"/items/v1/brands"
        return self._send("GET", path, body)

    def items_getbrands_v2(self, body: Any = None) -> Any:
        path = f"/items/v2/brands"
        return self._send("GET", path, body)

    def items_getcategories_v1(self, body: Any = None) -> Any:
        path = f"/items/v1/categories"
        return self._send("GET", path, body)

    def items_getcategories_v2(self, body: Any = None) -> Any:
        path = f"/items/v2/categories"
        return self._send("GET", path, body)

    def items_getfile_v2(self, id: str, body: Any = None) -> Any:
        path = f"/items/v2/file/{id}"
        return self._send("GET", path, body)

    def items_getinactive_v1(self, body: Any = None) -> Any:
        path = f"/items/v1/inactive"
        return self._send("GET", path, body)

    def items_getinactive_v2(self, body: Any = None) -> Any:
        path = f"/items/v2/inactive"
        return self._send("GET", path, body)

    def items_getphoto_v1(self, id: str, body: Any = None) -> Any:
        path = f"/items/v1/photo/{id}"
        return self._send("GET", path, body)

    def items_getphoto_v2(self, id: str, body: Any = None) -> Any:
        path = f"/items/v2/photo/{id}"
        return self._send("GET", path, body)

    def items_update_v2(self, body: Optional[List[ItemsUpdateV2RequestItem]] = None) -> Any:
        path = f"/items/v2"
        return self._send("PUT", path, body)

    def items_updatebrand_v2(self, body: Optional[List[ItemsUpdatebrandV2RequestItem]] = None) -> Any:
        path = f"/items/v2/brand"
        return self._send("PUT", path, body)

