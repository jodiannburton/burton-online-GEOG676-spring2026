import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "Toolbox"
        self.alias = ""
        self.tools = [BuildingProximity]

class BuildingProximity(object):
    def __init__(self):
        self.label = "Building Proximity"
        self.description = "Determines which buildings on TAMU's campus are near a targeted building"
        self.canRunInBackground = False
        self.category = "Building Tools"

    def getParameterInfo(self):
        p0 = arcpy.Parameter(displayName="GDB Folder", name="GDBFolder",
                             datatype="DEFolder", parameterType="Required", direction="Input")
        p1 = arcpy.Parameter(displayName="GDB Name", name="GDBName",
                             datatype="GPString", parameterType="Required", direction="Input")
        p2 = arcpy.Parameter(displayName="Garage CSV File", name="GarageCSVFile",
                             datatype="DEFile", parameterType="Required", direction="Input")
        p3 = arcpy.Parameter(displayName="Garage Layer Name", name="GarageLayerName",
                             datatype="GPString", parameterType="Required", direction="Input")
        p4 = arcpy.Parameter(displayName="Campus GDB", name="GDB",
                             datatype="DEWorkspace", parameterType="Required", direction="Input")
        p5 = arcpy.Parameter(displayName="Buffer Distance", name="BufferDistance",
                             datatype="GPDouble", parameterType="Required", direction="Input")
        return [p0, p1, p2, p3, p4, p5]

    def isLicensed(self):
        return True

    def execute(self, parameters, messages):
        folder_path = r'C:\Users\jodia\Downloads\TAMUG_Class\GEOG676_GISProgram\Github_repo\burton-online-GEOG676-spring2026\Lab_4'
        gdb_name = 'Test.gdb'
        gdb_path = folder_path + '\\' + gdb_name
        campus = r'C:\Users\jodia\Downloads\TAMUG_Class\GEOG676_GISProgram\Github_repo\burton-online-GEOG676-spring2026\Lab_4\Campus.gdb'
        csv_path = r'C:\Users\jodia\Downloads\TAMUG_Class\GEOG676_GISProgram\Github_repo\burton-online-GEOG676-spring2026\Lab_4\garages.csv'
        garage_layer_name = 'Garage_Points'

        arcpy.env.overwriteOutput = True

        if not arcpy.Exists(gdb_path):
            arcpy.management.CreateFileGDB(folder_path, gdb_name.replace(".gdb", ""))

        buildings_campus = campus + r'\Structures'
        buildings = gdb_path + r'\Buildings'
        arcpy.management.Copy(buildings_campus, buildings)

        wgs84 = arcpy.SpatialReference(4326)
        garages_layer = "garages"
        arcpy.management.MakeXYEventLayer(csv_path, "X", "Y", garages_layer, wgs84)
        arcpy.conversion.FeatureClassToFeatureClass(garages_layer, gdb_path, garage_layer_name)

        garage_points = gdb_path + '\\' + garage_layer_name
        spatial_ref = arcpy.Describe(buildings).spatialReference

        garage_reproj = gdb_path + r'\Garage_Points_reprojected'
        arcpy.management.Project(garage_points, garage_reproj, spatial_ref)

        garage_buffer = gdb_path + r'\Garage_Points_buffered'
        arcpy.analysis.Buffer(garage_reproj, garage_buffer, "150 Meters")

        intersection_fc = gdb_path + r'\Garage_Building_Intersection'
        arcpy.analysis.Intersect([garage_buffer, buildings], intersection_fc, "ALL")

        arcpy.conversion.TableToTable(intersection_fc, r'C:\Users\jodia\Downloads\TAMUG_Class\GEOG676_GISProgram\Github_repo\burton-online-GEOG676-spring2026\Lab_4', 'nearbyBuildings.csv')
        return None