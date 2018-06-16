import numpy as np
import py2gcode.gcode_cmd as gcode_cmd
import py2gcode.cnc_path as cnc_path
import py2gcode.cnc_routine as cnc_routine


class ArcRoutine(cnc_routine.SafeZRoutine):

    def __init__(self,param):
        super(ArcRoutine,self).__init__(param)

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
        
        maxCutDepth = self.param['maxCutDepth']
        angles = self.param['angles']
        radius = self.param['radius']
        depth = self.param['depth']
        if callable(self.param['radius']):
            radius_func = self.param['radius']
        else:
            print('not callable')
            radius_func = lambda z : radius

        # Move to safe height, then to start x,y and then to start z
        self.addStartComment()
        self.addRapidMoveToSafeZ()
        self.addRapidMoveToPos(x=cx,y=cy,comment='center x,y')
        self.addDwell(startDwell)

        stopZ = startZ - depth
        prevZ = startZ
        currZ = max([startZ - 0.5*maxCutDepth, stopZ])

        done = False
        passCnt = 0
        anglesRev = list(reversed(angles))

        x = cx + radius_func(currZ)*np.cos(np.deg2rad(angles[0]))
        y = cy + radius_func(currZ)*np.sin(np.deg2rad(angles[0]))
        self.addRapidMoveToSafeZ()
        self.addRapidMoveToPos(x=x,y=y,comment='start x,y')
        self.addDwell(startDwell)
        self.addMoveToStartZ()
        moveToStartCmd = gcode_cmd.LinearFeed(x=x,y=y)
        self.listOfCmds.append(moveToStartCmd)

        while not done:
            passCnt+=1
            self.addComment('arc {0} {1} '.format(passCnt,'ccw'))
            leadInPath = cnc_path.CircArcPath(
                    (cx,cy),
                    radius_func(currZ),
                    ang=angles,
                    plane='xy',
                    direction = 'ccw',
                    helix=(prevZ,currZ)
                    )
            self.listOfCmds.extend(leadInPath.listOfCmds)

            self.addComment('arc {0} {1} '.format(passCnt,'cw'))
            arcPath = cnc_path.CircArcPath(
                    (cx,cy),
                    radius_func(currZ),
                    ang=anglesRev,
                    plane='xy',
                    direction = 'cw',
                    helix=(currZ,currZ)
                    )
            self.listOfCmds.extend(arcPath.listOfCmds)

            # Get next z position
            if currZ <= stopZ:
                done = True
            prevZ = currZ
            currZ = max([currZ - 0.5*maxCutDepth, stopZ])

        # Move to safe z and add end comment
        self.addRapidMoveToSafeZ()
        self.addEndComment()
