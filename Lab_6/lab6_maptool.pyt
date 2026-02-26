import arcpy
import time  #needed to define the time.sleep part

class Toolbox(object):
    """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
    def __init__(self):
        self.label = "lab6_maptool"
        self.alias = "lab6_maptool"
        # List tool classes associated with the toolbox
        self.tools = [GraduatedColorsRenderer]

class GraduatedColorsRenderer(object):
    def __init__(self):
        self.label = "graduatedcolor"
        self.description = "Apply Graduated Colors to a selected layer"
        self.canRunInBackground = False
        self.category = "MapTools"

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # original project name
        aprx = arcpy.Parameter(
            displayName="Input ArcGIS Pro Project Name",
            name="aprxInputName",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        
        # which layer you want to classify to create colour map
        layer = arcpy.Parameter(
            displayName="Layer to Classify",
            name="LayerToClassify",
            datatype="GPLayer",
            parameterType="Required",
            direction="Input")
        
        # output folder location
        out_folder = arcpy.Parameter(
            displayName="Output Location",
            name="out_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        
        out_name = arcpy.Parameter(
            displayName="Output Project Name",
            name="out_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        return [aprx, layer, out_folder, out_name]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):

        aprx_path = parameters[0].valueAsText
        target_layer = parameters[1].valueAsText
        out_folder = parameters[2].valueAsText
        out_name = parameters[3].valueAsText

        if not out_name.lower().endswith(".aprx"):
            out_name += ".aprx"

        # project file
        project = arcpy.mp.ArcGISProject(aprx_path)
        
        # grabs first instance of a map from the .aprx
        campus = project.listMaps()[0]

        # Define progressor variables
        start = 0          # beginning position of the progressor
        step = 33          # the progress interval to move the progressor
        readTime = 0.5     # the time for users to read the progress 

        # Setup Progressor 
        arcpy.SetProgressor("step", "Processing...", 0, 100, step)

        #Increment Progressor
        arcpy.SetProgressorPosition(start + step) #it is now 33% completed
        arcpy.SetProgressorLabel("Finding your map layer...")
        time.sleep(readTime)  #pause the execution for 3 seconds
        # Add message to the results pane
        arcpy.AddMessage("Finding your map layer...")

        # Loop through the layers of the map
        for layer in campus.listLayers():
            # Check if the Layer is a feature layer
            if layer.isFeatureLayer:
                # Copy the layer's symbology
                symbology = layer.symbology
                # make sure the symbology has renderer attribute
                if hasattr(symbology, "renderer"):
                    # Check layer name
                    if layer.name == target_layer:

                        #Increment progressor
                        arcpy.SetProgressorPosition(start + step * 2)  #it is now 66% completed
                        arcpy.SetProgressorLabel("Calculating and classifying...")
                        time.sleep(readTime)
                        arcpy.AddMessage("Calculating and classifying...")

                        # Update the copy's renderer to "Graduated Colors Renderer"
                        symbology.updateRenderer("GraduatedColorsRenderer")
                        field_names = [f.name for f in arcpy.ListFields(layer)]
                        # Tell arcpy which field we want to base our chloropleth off of
                        if "Shape_Area" in field_names:
                             symbology.renderer.classificationField = "Shape_Area"
                        elif "Shape_Length" in field_names:
                             symbology.renderer.classificationField = "Shape_Length"

                        else:
                            symbology.renderer.classificationField = layer.describe("dataSource").OIDFieldName if hasattr(layer, "dataSource") else "OBJECTID"
                        # Set how many classes we'll have for the map
                        symbology.renderer.breakCount = 5
                        ramps = project.listColorRamps("Oranges")
                        if ramps:
                            symbology.renderer.colorRamp = ramps[0]
                        #Set the layer's actual symbology equal to the copy's
                        layer.symbology = symbology

        arcpy.SetProgressorPosition(100) # it is now 99% complete
        arcpy.SetProgressorLabel("Saving...")
        time.sleep(readTime)

        out_path = out_folder + "\\" + out_name
        project.saveACopy(out_path)

        arcpy.AddMessage("Finished Generating Layer...")