from enum import Enum


class MeasureAnalyseColumns(Enum):
    ObjectPath = "Full object path in IMX structure"
    ObjectPuic = "PUIC (unique identifier) of the object"
    ObjectName = "Human-readable name of the object"
    RefField = "Field used to reference the rail connection"
    RefFieldValue = "PUIC of the referenced rail connection"
    RefFieldName = "Name of the referenced rail connection"
    MeasureType = "Measure type at, from or to measure"
    ImxMeasure = "Original atMeasure value from IMX data"
    Calculated3DMeasure = "Calculated 3D measure along the rail geometry"
    DiffDistance3D = "Absolute difference between IMX and calculated 3D measure"
    Calculated2DMeasure = "Calculated 2D projected distance along the rail geometry"
    DiffDistance2D = "Absolute difference between IMX and calculated 2D distance"
