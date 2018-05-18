from __future__ import print_function
import py2gcode.gcode_cmd as gcode_cmd
import py2gcode.cnc_path as cnc_path
import py2gcode.cnc_routine as cnc_routine


class SphereFinishingRoutine(cnc_routine.SafeZRoutine):

    def __init__(self,param):
        super(SphereFinishingRoutine,self).__init__(param)

    def makeListOfCmds(self):
        # Retreive numerical parameters and convert to float 
        cx = float(self.param['centerX'])
        cy = float(self.param['centerY'])
        startZ = float(self.param['startZ'])
        try:
            startDwell = self.param['startDwell']
        except KeyError:
            startDwell = 0.0
        startDwell = abs(float(startDwell))

        toolpathData = self.param['toolpathData']
        x0 = cx + toolpathData[0]['radius']
        y0 = cy

        # Move to safe height, then to start x,y and then to start z
        self.addStartComment()
        self.addRapidMoveToSafeZ()
        self.addRapidMoveToPos(x=x0,y=y0,comment='start x,y')
        self.addDwell(startDwell)
        self.addMoveToStartZ()

        # Get z cutting parameters 
        prevZ = startZ

        for i, data in enumerate(toolpathData):
            x0 = cx + data['radius']
            y0 = cy
            currZ = data['step_z']

            #print('xx', data['radius'])
            #self.listOfCmds.append(gcode_cmd.LinearFeed(z=currZ))
            #moveToStartCmd = gcode_cmd.LinearFeed(x=x0,y=y0)
            #self.listOfCmds.append(moveToStartCmd)

            # Spiral Down
            self.addComment('leadin {0} '.format(i))
            moveToStartCmd = gcode_cmd.LinearFeed(x=x0,y=y0)
            self.listOfCmds.append(moveToStartCmd)
            leadInPath = cnc_path.CircPath(
                    (cx,cy),
                    data['radius'],
                    startAng=0,
                    plane='xy',
                    direction=self.param['direction'],
                    turns=1,
                    helix=(prevZ,currZ)
                    )
            self.listOfCmds.extend(leadInPath.listOfCmds)

            # Cut circle
            self.addComment('cirle {0} '.format(i))
            circPath = cnc_path.CircPath(
                    (cx,cy),
                    data['radius'],
                    startAng=0,
                    plane='xy',
                    direction=self.param['direction'],
                    turns=1
                    )
            self.listOfCmds.extend(circPath.listOfCmds)
            prevZ = currZ

        # Move to safe z and add end comment
        self.addRapidMoveToSafeZ()
        self.addEndComment()
