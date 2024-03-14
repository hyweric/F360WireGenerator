"""
Eric H. Nov 2023 
Generates a wire between two points with a random path. 
    Code Snippets - F360 UI Button/Timeline grouping code from GFGearGenerator Github
"""
import adsk.core, adsk.fusion, adsk.cam, traceback, random, math, os

ui = None
tbPanel = None
radius = 0.5
varc = 1
iterations = 10
handlers = []

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            mainAction(app)
        except:
            if ui:
                # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                pass

class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__() 
        
    def notify(self, args):
        try:
            cmd = args.command                  
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            if ui:
                # ui.messageBox('Panel command created failed: {}'.format(traceback.format_exc()))
                pass

def run(context):
    ui = None
    try: 
        app = adsk.core.Application.get() # derived button code from GFGearGen
        ui = app.userInterface
        workSpace = ui.workspaces.itemById('FusionSolidEnvironment')
        tbPanels = workSpace.toolbarPanels

        global tbPanel
        tbPanel = tbPanels.itemById('Panel')
        if tbPanel:
            tbPanel.deleteMe()

        tbPanel = tbPanels.add('Panel', 'Wire Generator', 'SelectPanel', False)

        cmdDef =ui.commandDefinitions.itemById('NC1')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef=ui.commandDefinitions.addButtonDefinition('NC1', 'Wire Generator', 'Generate a wire with 2 points.','Resources/wireIMG')

        cmdDefcontrol=tbPanel.controls.addCommand(cmdDef)
        cmdDefcontrol.isPromotedByDefault=True
        cmdDefcontrol.isPromoted=True
        cmdDefPressed=CommandCreatedEventHandler()
        cmdDef.commandCreated.add(cmdDefPressed)
        handlers.append(cmdDefPressed)
    except:
        if ui:
            # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            pass

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if tbPanel:
            tbPanel.deleteMe()
    except:
        if ui:
            # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            pass

def mainAction(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        cmdDef = ui.commandDefinitions.itemById('dialogCommand')
        if cmdDef: # caching issue go brr 
            cmdDef.deleteMe()

        cmdDef = ui.commandDefinitions.addButtonDefinition('dialogCommand', 'Wire Generator', 'Generate a Wire')

        onCommandCreated = HandlerOneCreation(app.activeProduct.rootComponent)
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        cmdDef.execute()
        adsk.autoTerminate(False)

    except:
        if ui:
            # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            pass

class HandlerOneCreation(adsk.core.CommandCreatedEventHandler):
    def __init__(self, comp):
        super().__init__()
        self.comp = None
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface

            cmd = args.command
            inputs = cmd.commandInputs  
            inputs.addSelectionInput('startPoint', 'Start Point', 'Select the start point')
            inputs.addSelectionInput('endPoint', 'End Point', 'Select the end point')

            inputs.addSelectionInput('plane', 'Plane', 'Select the plane the sketch of the start and end points were created on.')

            dropdown = inputs.addDropDownCommandInput('num_points', 'Number of Points', adsk.core.DropDownStyles.TextListDropDownStyle)
            dropdown.listItems.add('1', True)
            dropdown.listItems.add('2', False)
            dropdown.listItems.add('3', False)

            advancedGroup = inputs.addGroupCommandInput('advancedOptionsGroup', 'Advanced')
            advancedGroup.isExpanded = True

            # inputs.addValueInput('radius', 'Wire Radius (mm)', '', adsk.core.ValueInput.createByReal(radius))
            advancedGroup.children.addValueInput('radius', 'Wire Radius (mm)', '', adsk.core.ValueInput.createByReal(radius))
            advancedGroup.children.addValueInput('varc', 'Spread', '', adsk.core.ValueInput.createByReal(varc))
            advancedGroup.children.addValueInput('iterations', 'Iterations', '', adsk.core.ValueInput.createByReal(10))
            advancedGroup.children.addValueInput('angle', 'Angle (Vertical - 0 deg)', '', adsk.core.ValueInput.createByReal(0))
            advancedGroup.children.addValueInput('angle_variance', 'Angle Variance', '', adsk.core.ValueInput.createByReal(90))
            advancedGroup.children.addValueInput('dist_from_midpoint', 'Distance from Midpoint', '', adsk.core.ValueInput.createByReal(0.5))
            
            # Reminder: the plane selected MUST be the plane on which the start and end points were created, otherwise axis go brr 
            
            # Checkbox for the sweep option
            advancedGroup.children.addBoolValueInput('sweep', 'Disable Sweep', True)

            onExecute = HandlerOneAction(self.comp)
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            if ui:
                # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                pass

class HandlerOneAction (adsk.core.CommandEventHandler):
    def __init__(self, comp):
        super().__init__()
        self.splines = []
        self.comp = comp

    def notify(self, args):
        global radius; 
        global sweep; 
        ui = None
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface

            cmd = args.command
            inputs = cmd.commandInputs

            self.comp = app.activeProduct.rootComponent
            sketches = self.comp.sketches
            
            # retrieve inputs 
            
            radius = inputs.itemById('radius').value
            varc = inputs.itemById('varc').value
            iterations = inputs.itemById('iterations').value
            angle = inputs.itemById('angle').value
            angle_variance = inputs.itemById('angle_variance').value
            sweep = inputs.itemById('sweep').value
            scaled_dist_from_midpoint = inputs.itemById('dist_from_midpoint').value
            num_points = int(inputs.itemById('num_points').selectedItem.name)

            startPoint = inputs.itemById('startPoint').selection(0).entity
            endPoint = inputs.itemById('endPoint').selection(0).entity
            
            plane = inputs.itemById('plane').selection(0).entity

            # error handling for vertices 
            if not (isinstance(startPoint, adsk.fusion.SketchPoint) and isinstance(endPoint, adsk.fusion.SketchPoint)):
                if ui:
                    ui.messageBox('Please select points (not vertices).')
                return

            if plane.objectType == adsk.fusion.BRepFace.classType():
                face = adsk.fusion.BRepFace.cast(plane)
                sketch = sketches.add(face)
            else:
                sketch = sketches.add(plane)

            start = adsk.fusion.SketchPoint.cast(startPoint).geometry
            end = adsk.fusion.SketchPoint.cast(endPoint).geometry

            for _ in range(int(iterations)):    
                points = adsk.core.ObjectCollection.create()
                points.add(start)
                
                midpoint = adsk.core.Point3D.create((start.x + end.x) / 2, (start.y + end.y) / 2, (start.z + end.z) / 2)               
                for _ in range(num_points):   
                    point = rand_point(midpoint, sketch, varc, angle, angle_variance, start, end, scaled_dist_from_midpoint)
                    points.add(point)
                
                points.add(end)
                spline = sketch.sketchCurves.sketchFittedSplines.add(points)

                self.splines.append(spline)

            cmdDef2 = ui.commandDefinitions.itemById('selectSplineCommand')
            if not cmdDef2:
                cmdDef2 = ui.commandDefinitions.addButtonDefinition('selectSplineCommand', 'Select Spline', 'Select the spline')

            onCommandCreated2 = SplineHandlerCreation(self.splines, self.comp)
            cmdDef2.commandCreated.add(onCommandCreated2)
            handlers.append(onCommandCreated2)

            cmdDef2.execute()
        except:
            if ui:
                # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                pass

class SplineHandlerCreation(adsk.core.CommandCreatedEventHandler):
    def __init__(self, splines, comp):
        super().__init__()
        self.splines = splines
        self.comp = comp

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface

            cmd = args.command
            inputs = cmd.commandInputs

            inputs.addSelectionInput('spline', 'Select a Spline', 'Select the spline')

            onExecute2 = SplineHandlerAction(self.splines, self.comp)
            cmd.execute.add(onExecute2)
            handlers.append(onExecute2)
        except:
            if ui:
                # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                pass

class SplineHandlerAction(adsk.core.CommandEventHandler):
    def __init__(self, splines, comp):
        super().__init__()
        self.splines = splines
        self.comp = comp

    def notify(self, args):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface

            cmd = args.command
            inputs = cmd.commandInputs

            selected_spline = inputs.itemById('spline').selection(0).entity

            if not sweep:  # Only perform the sweep operation if the checkbox is checked
                sweep_path(selected_spline, self.comp)

            # delete other instances
            for spline in self.splines:
                if spline != selected_spline:
                    spline.deleteMe()
            groupTimeline(4)
        except:
            if ui:
                # ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                pass

# group timeline code from GF Gear Generator
def groupTimeline(elements): # last elements 
    app = adsk.core.Application.get()
    design = app.activeProduct
    tgroup = design.timeline.timelineGroups
    if design.timeline.count >= (elements+1):
        index = design.timeline.count - elements
    else:
        index = 0
    tgroup.add(index, design.timeline.count - 1)
    
def rand_point(midpoint, sketch, varc, angle, angle_variance, start, end, scaled_dist_from_midpoint):
    distance = math.sqrt((start.x - end.x) ** 2 + (start.y - end.y) ** 2 + (start.z - end.z) ** 2)
    start_end_line = sketch.sketchCurves.sketchLines.addByTwoPoints(start,end) 
    start_end_line.isConstruction = True

    # Create a perpendicular line off of line1 starting from the midpoint
    perpendicular_line = sketch.sketchCurves.sketchLines.addByTwoPoints(midpoint, adsk.core.Point3D.create(midpoint.x + distance * scaled_dist_from_midpoint, midpoint.y, midpoint.z))    
    perpendicular_line.isConstruction = True

    constraints = sketch.geometricConstraints
    coincidentConstraint = constraints.addCoincident(perpendicular_line.startSketchPoint, start_end_line)
    midpointConstraint = constraints.addMidPoint(perpendicular_line.startSketchPoint, start_end_line)
    perpConstraint = constraints.addPerpendicular(start_end_line, perpendicular_line) # order of constraints MATTERS so sketch does not shift 

    angle_rad = math.radians(angle + random.uniform(-angle_variance, angle_variance)) # angle in radians w/ variation

    n = adsk.core.Vector3D.create(end.x - start.x, end.y - start.y, end.z - start.z) # start to end vector 
    n.normalize() # normalize the vector (magnitude one, direction maintained)

    vectorPerpLine = adsk.core.Vector3D.create(perpendicular_line.endSketchPoint.geometry.x - perpendicular_line.startSketchPoint.geometry.x,perpendicular_line.endSketchPoint.geometry.y - perpendicular_line.startSketchPoint.geometry.y, perpendicular_line.endSketchPoint.geometry.z - perpendicular_line.startSketchPoint.geometry.z)

    verticalVector = adsk.core.Vector3D.create(0,1,0)
    verticalVector.normalize()
    
    angle_to_vertical = vectorPerpLine.angleTo(verticalVector) # angle between the perpendicular line and the vertical vector
    
    # Align the perpendicular line to the vertical vector
    cross_product = vectorPerpLine.crossProduct(verticalVector)
    dot_product = cross_product.dotProduct(n)
    if dot_product < 0: # checking z direction of cross product
        angle_to_vertical = -angle_to_vertical
        
    # rotate to vertical + desired angle
    vPrime_x, vPrime_y, vPrime_z = rodriguez_rotation(angle_to_vertical - angle_rad, n, vectorPerpLine)
    # vPrime_x, vPrime_y, vPrime_z = rodriguez_rotation(angle_to_vertical, n, vectorPerpLine) #rotate to vertical

    # add variation 
    vPrime_x = vPrime_x + random.uniform(-varc * 2, varc * 2)
    vPrime_y = vPrime_y + random.uniform(-varc * 2, varc * 2)
    vPrime_z = vPrime_z + random.uniform(-varc * 2, varc * 2)

    # create the new vector 
    vPrime = adsk.core.Vector3D.create(vPrime_x, vPrime_y, vPrime_z) # Can skip this step and just use vector coordinates directly  

    endOfvPrime = adsk.core.Point3D.create(vPrime.x + perpendicular_line.startSketchPoint.geometry.x, vPrime.y + perpendicular_line.startSketchPoint.geometry.y, vPrime.z + perpendicular_line.startSketchPoint.geometry.z)
    
    perpendicular_line.deleteMe()
    start_end_line.deleteMe()

    return endOfvPrime

def rodriguez_rotation(angle, n, v): # Rodrigues' rotation formula
    n_x, n_y, n_z = n.x, n.y, n.z # Decompose vector into components

    x_comp = (1- math.cos(angle))* (v.dotProduct(n)) * n_x + math.cos(angle) * v.x + math.sin(angle) * (n.crossProduct(v)).x
    y_comp = (1- math.cos(angle))* (v.dotProduct(n)) * n_y + math.cos(angle) * v.y + math.sin(angle) * (n.crossProduct(v)).y
    z_comp = (1- math.cos(angle))* (v.dotProduct(n)) * n_z + math.cos(angle) * v.z + math.sin(angle) * (n.crossProduct(v)).z
    return x_comp, y_comp, z_comp

def sweep_path(selected_spline, comp):
    try:
        sketches = comp.sketches
        
        # get path from the selected spline
        path = comp.features.createPath(selected_spline)
        
        # Construction plane on path 
        planeInput = comp.constructionPlanes.createInput()
        planeInput.setByDistanceOnPath(path, adsk.core.ValueInput.createByReal(0))
        plane = comp.constructionPlanes.add(planeInput)
        
        # Sketch Circle on construction plane
        sketch = sketches.add(plane)
        center = plane.geometry.origin
        center = sketch.modelToSketchSpace(center)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius/20)
        
        # sweep feature using the profile and path
        profile = sketch.profiles[0]
        sweepFeats = comp.features.sweepFeatures
        sweepInput = sweepFeats.createInput(profile, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweepInput.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        sweepFeat = sweepFeats.add(sweepInput)
        return sweepFeat
    except:
        return None
