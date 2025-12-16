from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime, timezone
from sqlalchemy import DateTime
db = SQLAlchemy()

# Base class for all elements
class Element(db.Model):
    __tablename__ = 'elements'
    __table_args__ = {'schema': 'sfrs_component_database'}  
    id = db.Column(db.Integer, primary_key=True)
    
    element_name = db.Column(db.String(20), nullable=False)
    location_name = db.Column(db.String(20))
    is_detector = db.Column(db.Boolean, default=False)
    high_energy_branch = db.Column(db.Boolean, nullable=False, default=False)
    low_energy_branch = db.Column(db.Boolean, nullable=False, default=False)
    ring_branch = db.Column(db.Boolean, nullable=False, default=False)
    length = db.Column(db.Float, nullable=True)
    type = db.Column(db.String(25), nullable=False)  # Discriminator column
    
    __mapper_args__ = {
        'polymorphic_identity': 'element',
        'polymorphic_on': type
    }

    aperture = db.relationship(
        "Aperture",
        uselist=False,
        back_populates="element"
    )

    plm = db.relationship(
        "Plm",
        uselist=False,
        back_populates="element"
    )

class Plm(db.Model):
    __tablename__ = 'plm'
    __table_args__ = {'schema': 'sfrs_component_database'}

    id = db.Column(db.Integer, primary_key=True)

    element_id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.elements.id'),
        unique=True,
        nullable=False
    )

    last_update = db.Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=True)

    plm_comp_cid=db.Column(db.String(15), unique=True, nullable=True)
    plm_comp_cid_desc=db.Column(db.String(50), nullable=True)
    plm_comp_cid_parent=db.Column(db.String(15), nullable=True)
    plm_comp_aid=db.Column(db.String(11), nullable=True)
    plm_comp_sid_desc=db.Column(db.String(50), nullable=True)
    plm_comp_psp=db.Column(db.String(50), nullable=True)
    plm_comp_manufact=db.Column(db.String(50), nullable=True)
    plm_comp_manufact_country=db.Column(db.String(50), nullable=True)
    plm_comp_status=db.Column(db.String(4), nullable=True)
    plm_comp_status_description=db.Column(db.String(50), nullable=True)
    plm_comp_location=db.Column(db.String(50), nullable=True)
    plm_comp_manufact_serial=db.Column(db.String(50), nullable=True)
    plm_comp_wp=db.Column(db.String(50), nullable=True)
    plm_comp_order_no=db.Column(db.String(50), nullable=True)
    plm_comp_edms=db.Column(db.String(50), nullable=True)
    plm_comp_contract_no=db.Column(db.String(50), nullable=True)
    #plm_comp_system_id=db.Column(db.String(50))

    plm_log_contact=db.Column(db.String(50), nullable=True)
    plm_log_width=db.Column(db.String(50), nullable=True)
    plm_log_weight=db.Column(db.String(50), nullable=True)
    plm_log_height=db.Column(db.String(50), nullable=True)
    plm_log_length=db.Column(db.String(50), nullable=True)
    plm_log_storage_cond=db.Column(db.String(50), nullable=True)
    plm_log_tariff_exempt=db.Column(db.String(50), nullable=True)
    plm_log_deliv_loc=db.Column(db.String(50), nullable=True)
    plm_log_deliv_date=db.Column(db.String(50), nullable=True)
    plm_log_maintenance=db.Column(db.String(50), nullable=True)
    plm_log_constr_loc=db.Column(db.String(50), nullable=True)
    plm_log_final_loc=db.Column(db.String(50), nullable=True)
    plm_log_install_date=db.Column(db.String(50), nullable=True)
    plm_log_tariff_no=db.Column(db.String(50), nullable=True)
    plm_log_goodsin_date=db.Column(db.String(50), nullable=True)

    element = db.relationship("Element", back_populates="plm")

class Aperture(db.Model):
    __tablename__ = 'apertures'
    __table_args__ = {'schema': 'sfrs_component_database'}

    id = db.Column(db.Integer, primary_key=True)

    element_id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.elements.id'),
        unique=True,
        nullable=False
    )

    # "circle", "rectangle", "complex"
    shape_type = db.Column(db.String(20), nullable=False)

    # --------------- Circle ---------------
    radius = db.Column(db.Float, nullable=True)

    # --------------- Rectangle ---------------
    rect_width = db.Column(db.Float, nullable=True)
    rect_height = db.Column(db.Float, nullable=True)

    # --------------- Complex shape ---------------
    polygon_points = db.Column(db.JSON, nullable=True)

    element = db.relationship("Element", back_populates="aperture")

    @validates('shape_type')
    def validate_shape(self, key, value):
        if value not in ("circle", "rectangle", "octogon", "complex"):
            raise ValueError("shape_type must be one of: circle, rectangle, complex")
        return value

    @validates('radius', 'rect_width', 'rect_height', 'polygon_points')
    def validate_geometry(self, key, value):
        if self.shape_type == "circle" and key == "radius" and (value is None or value <= 0):
            raise ValueError("Circle aperture must have a positive radius")
        if self.shape_type == "rectangle" and key in ("rect_width", "rect_height") and (value is None or value <= 0):
            raise ValueError("Rectangle aperture must have positive width and height")
        if self.shape_type == "complex" and key == "polygon_points" and (not value or not isinstance(value, list)):
            raise ValueError("Complex aperture must have a list of polygon points")
        return value

    # ---------------- Helper method ----------------
    def get_profile(self):
        """Return a dict with the key geometry info depending on shape type."""
        if self.shape_type == "circle":
            return {"radius": self.radius}
        elif self.shape_type == "rectangle":
            return {"width": self.rect_width, "height": self.rect_height}
        elif self.shape_type == "complex":
            return {"points": self.polygon_points}
        else:
            return {}

class CryoFeedbox(Element):
    __tablename__ = 'cryo_feed_boxes'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    loc = db.Column(db.JSON, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'cryo_feed_box'
    }

class ExperimentalChamber(Element):
    __tablename__ = 'experimental_chambers'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    number_of_detectors = db.Column(db.Integer, nullable=False) 
    focal_plane = db.Column(db.String(4), nullable = False)
    __mapper_args__ = {
        'polymorphic_identity': 'experimental_chamber'
    }

class EmptyDetector(Element):
    __tablename__ = 'empty_detectors'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)

    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='empty_detectors',
        foreign_keys=[experimental_chamber_id]  
    )

    __mapper_args__ = {
        'polymorphic_identity': 'empty_detector'
    }

class BeamStopper(Element):
    __tablename__ = 'beam_stoppers'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    pneumatic_actuator_name = db.Column(db.String(15), nullable=False)

    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='beam_stoppers',
        foreign_keys=[experimental_chamber_id]   
    )

    __mapper_args__ = {
        'polymorphic_identity': 'beam_stopper'
    }

class ProfileGrid(Element):
    __tablename__ = 'profile_grids'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    grid_name = db.Column(db.String(15), nullable=False) 
    stepper_motor_name = db.Column(db.String(15), nullable=False) 
    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='profile_grids',
        foreign_keys=[experimental_chamber_id]   
    )
    __mapper_args__ = {
        'polymorphic_identity': 'profile_grid'
    }

class HorizontalSlit(Element):
    __tablename__ = 'horizontal_slits'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    left_slit_name = db.Column(db.String(15), nullable=False) 
    right_slit_name = db.Column(db.String(15), nullable=False) 
    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='horizontal_slits',
        foreign_keys=[experimental_chamber_id]   
    )
    __mapper_args__ = {
        'polymorphic_identity': 'horizontal_slit'
    }

class PlasticScintillator(Element):
    __tablename__ = 'plastic_scintillators'
    __table_args__ = {'schema': 'sfrs_component_database'}  
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    pneumatic_actuator = db.Column(db.String(15), nullable=False) 
    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='plastic_scintillators',
        foreign_keys=[experimental_chamber_id]   
    )
    __mapper_args__ = {
        'polymorphic_identity': 'plastic_scintillator'
    }

class RotaryWedgeDegrader(Element):
    __tablename__ = 'rotary_wedge_degraders'
    __table_args__ = {'schema': 'sfrs_component_database'}
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    stepper_motor = db.Column(db.String(15), nullable=False) 
    pneumatic_actuator = db.Column(db.String(15), nullable=False) 
    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='rotary_wedge_degraders',
        foreign_keys=[experimental_chamber_id]   
    )
    __mapper_args__ = {
        'polymorphic_identity': 'rotary_wedge_degrader'
    }

class SlidableWedgeDegrader(Element):
    __tablename__ = 'slidable_wedge_degraders'
    __table_args__ = {'schema': 'sfrs_component_database'}  
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    stepper_motor = db.Column(db.String(15), nullable=False)
    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='slidable_wedge_degraders',
        foreign_keys=[experimental_chamber_id]   
    )
    __mapper_args__ = {
        'polymorphic_identity': 'slidable_wedge_degrader'
    }

class LadderSystemDegrader(Element):
    __tablename__ = 'ladder_system_degraders'
    __table_args__ = {'schema': 'sfrs_component_database'}
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    slot_number = db.Column(db.Integer, nullable=True)
    stepper_motor = db.Column(db.String(15), nullable=False)
    # Foreign key to the experimental chamber
    experimental_chamber_id = db.Column(
        db.Integer, 
        db.ForeignKey('sfrs_component_database.experimental_chambers.id'), 
        nullable=True
    )

    # Disambiguated relationship
    experimental_chamber = db.relationship(
        'ExperimentalChamber',
        backref='ladder_system_degraders',
        foreign_keys=[experimental_chamber_id]   
    )
    __mapper_args__ = {
        'polymorphic_identity': 'ladder_system_degrader'
    }

# Derived class for Dipole
class Dipole(Element):
    __tablename__ = 'dipoles'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    loc = db.Column(db.JSON, nullable=True)
    bends_right = db.Column(db.Boolean, nullable = True)
    is_superconducting = db.Column(db.Boolean, nullable = True)
    bending_angle = db.Column(db.Float, nullable = True)
    bending_radius = db.Column(db.Float, nullable=True)
    magnetic_measurements = db.Column(db.PickleType, nullable=True)
    BDL_max = db.Column(db.Float, nullable=True)
    nominal_current = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'dipole'
    }

class Multiplett(Element):
    __tablename__ = 'multipletts'
    __table_args__ = {'schema': 'sfrs_component_database'}
    
    id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.elements.id'),
        primary_key=True
    )

    steerer = db.relationship('Steerer', back_populates='multiplett', foreign_keys='Steerer.multiplett_id')
    quadrupoles = db.relationship('Quadrupole', back_populates='multiplett', foreign_keys='Quadrupole.multiplett_id')
    sextupoles = db.relationship('Sextupole', back_populates='multiplett', foreign_keys='Sextupole.multiplett_id')
    octupoles = db.relationship('Octupole', back_populates='multiplett', foreign_keys='Octupole.multiplett_id')

    __mapper_args__ = {
        'polymorphic_identity': 'multiplett'
    }

# Derived class for Quadrupole
class Quadrupole(Element):
    __tablename__ = 'quadrupoles'
    __table_args__ = {'schema': 'sfrs_component_database'}  

    id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.elements.id'),
        primary_key=True
    )

    multiplett_id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.multipletts.id'),
        nullable=True
    )

    multiplett = db.relationship(
        'Multiplett',
        back_populates='quadrupoles',
        foreign_keys=[multiplett_id]
    )
    loc = db.Column(db.JSON, nullable=True)
    is_superconducting = db.Column(db.Boolean, nullable = True)
    is_horizontal_focusing = db.Column(db.Boolean, nullable=True)
    position_in_multiplett = db.Column(db.Integer, nullable = True)
    magnetic_measurements = db.Column(db.PickleType, nullable=True)
    GDL_max = db.Column(db.Float, nullable=True)
    nominal_current = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'quadrupole'
    }

# Derived class for Sextupoles
class Sextupole(Element):
    __tablename__ = 'sextupoles'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    multiplett_id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.multipletts.id'),
        nullable=True
    )

    multiplett = db.relationship(
        'Multiplett',
        back_populates='sextupoles',
        foreign_keys=[multiplett_id]
    )
    loc = db.Column(db.JSON, nullable=True)
    is_superconducting = db.Column(db.Boolean, nullable = True)
    position_in_multiplett = db.Column(db.Integer, nullable = True)
    magnetic_measurements = db.Column(db.PickleType, nullable=True)
    SDL_max = db.Column(db.Float, nullable=True)
    nominal_current = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'sextupole'
    }

# Derived class for Octupole
class Octupole(Element):
    __tablename__ = 'octupoles'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    multiplett_id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.multipletts.id'),
        nullable=True
    )

    multiplett = db.relationship(
        'Multiplett',
        back_populates='octupoles',
        foreign_keys=[multiplett_id]
    )
    loc = db.Column(db.JSON, nullable=True)
    is_superconducting = db.Column(db.Boolean, nullable = True)
    position_in_multiplett = db.Column(db.Integer, nullable = True)
    magnetic_measurements = db.Column(db.PickleType, nullable=True)
    ODL_max = db.Column(db.Float, nullable=True)
    nominal_current = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'octupole'
    }

# Derived class for Steerer
class Steerer(Element):
    __tablename__ = 'steerer'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    multiplett_id = db.Column(
        db.Integer,
        db.ForeignKey('sfrs_component_database.multipletts.id'),
        nullable=True
    )

    multiplett = db.relationship(
        'Multiplett',
        back_populates='steerer',
        foreign_keys=[multiplett_id]
    )
    loc = db.Column(db.JSON, nullable=True)
    is_superconducting = db.Column(db.Boolean, nullable = True)
    is_vertical_bending = db.Column(db.Boolean, nullable=True)
    position_in_multiplett = db.Column(db.Integer, nullable = True)
    magnetic_measurements = db.Column(db.PickleType, nullable=True)
    BDL_max = db.Column(db.Float, nullable=True)
    nominal_current = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'steerer'
    }

class Drift(Element):
    __tablename__ = 'beamlines'
    __table_args__ = {'schema': 'sfrs_component_database'} 
    loc = db.Column(db.JSON, nullable=True)
    id = db.Column(db.Integer, db.ForeignKey('sfrs_component_database.elements.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'drift'
    }

