##############################################################################
##
# This file is part of Sardana
##
# http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################
"""IcePAP linked axes module

    ┌───────────────────┐
    │   sardana-icepap  │
    ├───────────────────┤
    │     icepap lib    │
    ├───────────────────┤
    │     IcePAP FW     │
    └───────────────────┘

    Fig.1 — The IcePAP software stack

Modern IcePAP firmware provides support for grouping drivers into [linked
axes][1]. Key features;

* Prevents driving individual axes by protecting driver board level commands
* Synchronized motion stop/start
* Consolidated linked axis status register

Whilst linked axes are fully supported in FW, the python `icepap` library
provides no explicit support for them. One workaround is to leverage the
[alias][2] functionality of the `icepap` library. This allows strings to be
passed to system level IcePAP commands, e.g. linked axis names.

The Sardana controller for IcePAP, `sardana-icepap`, also provides no explicit
support for linked axes. Indeed, it makes extensive use of the `icepap.axis`
API, which leverages driver board commands. These are protected on linked
drivers, and cannot be used. One workaround is to instead use equivalent system
level commands where available.

This module applies these two workarounds to provide a Sardana motor controller
for IcePAP linked axes (`IcepapLinkedAxisController`).

[1]: https://icepap-organization.gitlab.io/icepap-user-manual/operation_instructions.html#linked-axes
[2]: https://gitlab.com/icepap-organization/IcePAP/-/blob/master/icepap/controller.py?ref_type=heads#L308

"""

from sardana_icepap.ctrl.IcePAPCtrl import IcepapController
import functools

def _axis2lnkname(wrapped):
    """Decorator to convert numeric axis argument to linked axis name

    * Asserts the axis (numeric) is part of a linked axis
    * Calls wrapped function with the linked axis name (string)

    """
    @functools.wraps(wrapped)
    def wrapper(self, axis, *args, **kwargs):
        try:
            if axis in self.lnknames.values():
                lnkname = axis
            else:
                lnkname = self.lnknames[axis]
        except KeyError:
            self._log.error(f"Axis {axis} is not linked")
        else:
            return wrapped(self, lnkname, *args, **kwargs)
    return wrapper

def _supermethod(wrapped):
    """Decorator to call superclass method of same name

    Usually this is handled by MRO, but is required here as we want to further
    decorate our inherited methods.

    """
    @functools.wraps(wrapped)
    def wrapper(self, *args, **kwargs):
        return getattr(
            super(type(self), self),
            wrapped.__name__
        )(*args, **kwargs)
    return wrapper

class IcepapLinkedAxisController(IcepapController):
    """Sardana motor controller for IcePAP linked axes

    This controller can be be considered a fairly thin wrapper around the
    'unlinked axis' controller (`IcepapController`). It implements;

    * Addition of `icepap` library aliases for all linked axes
    * Wrapping of Sardana controller methods with axis (numeric) to linked axis
      (string) names
    * Overriding/extending Sardana controller methods to use system level commands

    """

    lnknames = None
    """Axis (numeric) to linked axis name (string) mapping"""

    def __init__(self, inst, props, *args, **kwargs):

        # Superclass constructor
        super().__init__(
            inst,
            props,
            *args,
            **kwargs
        )                                            # Calls MotorController.__init__

        # Prune axis attributes
        self._init_axis_attributes()

        # Initialise linked axis names
        #
        #   Cache as instance member to avoid repeated queried to IcePAP
        #
        self._init_lnknames()
        self._log.debug(f"IcepapLinkedAxisController.lnknames: {self.lnknames}")

        # Add linked axes as IcePAPController aliases
        for lnkname in set(self.lnknames.values()):
            self.ipap.add_alias(lnkname, lnkname)

    def _init_axis_attributes(self):
        """Remove unavailable axis attributes

        Remove inherited axis attributes which are unavailable for linked axes

        """
        self.axis_attributes = self.axis_attributes.copy()
        self.axis_attributes.pop("PowerInfo")            # Board command only
        self.axis_attributes.pop("Indexer")              # Board functionality only
        self.axis_attributes.pop("InfoA")                # Board functionality only
        self.axis_attributes.pop("InfoB")                # Board functionality only
        self.axis_attributes.pop("InfoC")                # Board functionality only
        self.axis_attributes.pop("EnableEncoder_5V")     # Board functionality only
        self.axis_attributes.pop("ClosedLoop")           # Board functionality only
        self.axis_attributes.pop("MeasureI")             # Board functionality only
        self.axis_attributes.pop("StatusDetails")        # Board command only
        self.axis_attributes.pop("EcamDatTable")         # Board functionality only
        self.axis_attributes.pop("EcamOut")              # Board functionality only
        self.axis_attributes.pop("SyncAux")              # Board functionality only
        self.axis_attributes.pop("SyncPos")              # Board functionality only
        self.axis_attributes.pop("SyncRes")              # Board functionality only

    def _init_lnknames(self):
        """Populate linked axis name mapping from IcePAP query"""
        self.lnknames = {}
        lines = self.ipap.get_linked()
        if lines:
            for line in lines:
                words = line.split()
                lnkname = words[0]
                for axis in words[1:]:
                    self.lnknames[int(axis)] = lnkname

    @_axis2lnkname
    def GetAxisName(self, lnkname):
        axis = next(
            key
            for key, value in
            self.lnknames.items()
            if value == lnkname
        )
        return super().GetAxisName(axis)

    @_axis2lnkname
    def AddDevice(self, lnkname):
        if lnkname in self.attributes:
            self._log.warning(f"Axis {lnkname} already added (as linked axis '{lnkname}')")
        return super().AddDevice(lnkname)

    @_axis2lnkname
    def DeleteDevice(self, lnkname):
        if lnkname not in self.attributes:
            self._log.warning(f"Axis {lnkname} not added (as linked axis '{lnkname}')")
        return super().DeleteDevice(lnkname)

    @_axis2lnkname
    @_supermethod
    def PreStateOne(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def StateOne(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def PreReadOne(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def ReadOne(self, lnkname): pass

    @_axis2lnkname
    def StartOne(self, lnkname, pos):
        """Start single axis

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """
        spu = self.attributes[lnkname]["step_per_unit"]
        if not self.attributes[lnkname]['use_encoder_source']:
            desired_absolute_steps_pos = pos * spu
        else:
            try:
                current_source_pos = self.getEncoder(lnkname)
                #current_steps_pos = self.ipap[lnkname].pos         # NO — `icepap.axis` interface
                current_steps_pos = self.ipap.get_pos(lnkname)[0]   # YES — `icepap.controller` interface
            except Exception as e:
                self._log.error(f"StartOne({lnkname:d},{pos:f}).\nException:\n{str(e)}")
                return False
            pos_increment = pos - current_source_pos
            steps_increment = pos_increment * spu
            desired_absolute_steps_pos = current_steps_pos + steps_increment

        if self.attributes[lnkname]['move_in_group']:
            self.move_multiple_grouped.append(
                (lnkname, desired_absolute_steps_pos)
            )
        else:
            self.move_multiple_not_grouped.append(
                (lnkname, desired_absolute_steps_pos)
            )
        return True

    @_axis2lnkname
    def StopOne(self, lnkname):
        """Stop single axis

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """
        try:
            #factor = (
            #    self.ipap[lnkname].velocity
            #    / self.ipap[lnkname].acctime
            #)                                                  # NO — `icepap.axis` interface
            factor = (
                self.ipap.get_velocity(lnkname)[0]
                / self.ipap.get_acctime(lnkname)[0]
            )                                                   # YES — `icepap.controller` interface
        except Exception as e:
            msg = 'Problems while trying to determine velocity to ' + \
                  'acceleration factor'
            self._log.error(f"StopOne({lnkname:d}): {msg}. Trying to abort...")
            self._log.debug(e)
            self.AbortOne(lnkname)
            raise Exception(msg)
        if factor < 18:
            self.AbortOne(lnkname)
        else:
            self.stop_multiple.append(lnkname)

    @_axis2lnkname
    @_supermethod
    def AbortOne(self, lnkname): pass

    @_axis2lnkname
    def DefinePosition(self, lnkname, position):
        """Define motor position

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """
        step_pos = position * self.attributes[lnkname]['step_per_unit']
        #self.ipap[axis].pos = step_pos                         # NO — `icepap.axis` interface
        self.ipap.set_pos(
            [ (lnkname, step_pos) ]
        )                                                       # YES — `icepap.controller` interface

    @_axis2lnkname
    def _SetVelocity(self, lnkname, velocity_steps):
        """Set motor velocity and update acceleration time

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """
        #accel_time = self.ipap[axis].acctime
        #self.ipap[axis].velocity = velocity_steps
        #self.ipap[axis].acctime = accel_time                   # NO — `icepap.axis` interface

        accel_time = self.ipap.get_acctime(lnkname)[0]
        self.ipap.set_velocity(
            [ (lnkname, velocity_steps) ]
        )
        self.ipap.set_acctime(
            [ (lnkname, accel_time) ]
        )                                                       # YES — `icepap.controller` interface

    @_axis2lnkname
    def SetAxisPar(self, lnkname, name, value):
        """Set Motor axis standard parameters

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """
        _name = name.lower()
        if _name == "acceleration":
            #self.ipap[axis].acctime = value                    # NO — `icepap.axis` interface
            self.ipap.set_acctime(
                [ (lnkname, value) ]
            )                                                   # YES — `icepap.controller` interface
        else:
            return super().SetAxisPar(lnkname, name, value)

    @_axis2lnkname
    def GetAxisPar(self, lnkname, name):
        """Get Motor axis standard parameters

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """
        _name = name.lower()
        if _name == "velocity":
            spu = self.attributes[lnkname]['step_per_unit']
            #value = self.ipap[axis].velocity / spu             # NO — `icepap.axis` interface
            return self.ipap.get_velocity(lnkname)[0] / spu     # YES — `icepap.controller` interface
        elif _name in ("acceleration", "deceleration"):
            #value = self.ipap[axis].acctime                    # NO — `icepap.axis` interface
            return self.ipap.get_acctime(lnkname)[0]            # YES — `icepap.controller` interface
        else:
            return super().GetAxisPar(lnkname, name)

    # -------------------------------------------------------------------------
    #               Axis Extra Parameters
    # -------------------------------------------------------------------------

    @_axis2lnkname
    @_supermethod
    def getMoveInGroup(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def setMoveInGroup(self, lnkname, value): pass

    @_axis2lnkname
    @_supermethod
    def getAutoESYNC(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def setAutoESYNC(self, lnkname, value): pass

    @_axis2lnkname
    @_supermethod
    def getMotorEnabled(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def setMotorEnabled(self, lnkname, value): pass

    @_axis2lnkname
    @_supermethod
    def getUseEncoderSource(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def setUseEncoderSource(self, lnkname, value): pass

    @_axis2lnkname
    @_supermethod
    def getEncoderSource(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def setEncoderSource(self, lnkname, value): pass

    @_axis2lnkname
    @_supermethod
    def getEncoderSourceFormula(self, lnkname): pass

    @_axis2lnkname
    @_supermethod
    def setEncoderSourceFormula(self, lnkname, value): pass

    @_axis2lnkname
    @_supermethod
    def getEncoder(self, lnkname): pass

    @_axis2lnkname
    def GetAxisExtraPar(self, lnkname, name):
        """Get Motor axis extra parameters

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """

        _name = name.lower()

        # Status*
        state_methods = {
            "status5vpower": "is_5vpower",
            "statusalive": "is_alive",
            "statuspoweron": "is_poweron",
            "statusdisable": "is_disabled",
            "statushome": "is_inhome",
            "statusindexer": "get_indexer_str",
            "statusinfo": "get_info_code",
            "statuslimpos": "is_limit_positive",
            "statuslimneg": "is_limit_negative",
            "statusmode": "get_mode_str",
            "statusmoving": "is_moving",
            "statusoutofwin": "is_outofwin",
            "statuspresent": "is_present",
            "statusready": "is_ready",
            "statussettling": "is_settling",
            "statusstopcode": "get_stop_str",
            "statusstopcodevalue": "get_stop_code",
            "statusverserr": "is_verserr",
            "statuswarning": "is_warning",
        }
        if _name in state_methods:
            return getattr(
                self.ipap.get_states(lnkname)[0],
                state_methods[_name]
            )()

        # DifAxTgtEnc, DifAxShftEnc, DifAxMotor
        elif _name.startswith("difax"):
            return (
                self.ipap.get_pos(lnkname, "axis")[0]
                - self.ipap.get_pos(
                    lnkname,
                    _name.replace("difax","",1)
                )[0]
            )

        # VelMotor, VelCurrent
        elif _name.startswith("vel"):
            return (
                self.ipap.get_velocity(
                    lnkname,
                    _name.replace("vel","",1)
                )[0]
            )

        # PowerOn
        elif _name == "poweron":
            return self.ipap.get_power(lnkname)[0]

        # PosAxis, PosShftEnc, PosTgtEnc, PosEncIn, PosInPos, PosAbsEnc, PosMotor
        elif _name.startswith("pos"):
            return self.ipap.get_pos(
                lnkname,
                _name.replace("pos","",1)
            )[0]

        # EncAxis, EncShftEnc, EncTgtEnc, EncEncIn, EncInEnc, EncAbsEnc
        elif _name.startswith("enc"):
            return self.ipap.get_enc(
                lnkname,
                _name.replace("enc","",1)
            )[0]

        # StatusCode, StatusDriverBoard
        elif _name in ("statuscode", "statusdriverboard"):
            return (
                self.ipap.get_status(lnkname)[0]
            )

        # Unknown
        else:
            self._log.error(f"Unknown axis attribute ({name})")

    @_axis2lnkname
    def SetAxisExtraPar(self, lnkname, name, value):
        """Set Motor axis extra parameters

        Essentially same functionality as IcePAPCtrl, but using
        `icepap.controller` interface rather than `icepap.axis` interface

        """

        _name = name.lower()

        try:

            # PowerOn
            if _name == "poweron":
                self.ipap.set_power(lnkname, value)

            # Unknown
            else:
                self._log.error(f"Unknown axis attribute ({name})")

        except Exception as e:
            self._log.error(f"{_name} {str(e)}")

