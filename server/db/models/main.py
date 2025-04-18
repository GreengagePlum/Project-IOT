"""Database and schema creation script

Creates the sqlite database and its DDL schema also creating integrity checking triggers to enforce some constraints.
"""

from sqlalchemy import DDL
from sqlalchemy import event
from sqlalchemy import create_engine
from sensor import *

if __name__ == "__main__":

    led_check_trigger = DDL(
        """
        CREATE TRIGGER led_reading_newer_than_join_date
        BEFORE INSERT
        ON led_status
        FOR EACH ROW
        BEGIN
            -- Check if the reading timestamp is strictly greater than the sensor's joined timestamp
            SELECT
                CASE
                    WHEN (SELECT joined_at FROM sensor WHERE id = NEW.sensor_id) >= NEW.date
                    THEN RAISE(ABORT, 'Reading timestamp must be strictly after sensor joined timestamp')
            END;
        END;
    """
    )
    button_check_trigger = DDL(
        """
        CREATE TRIGGER button_reading_newer_than_join_date
        BEFORE INSERT
        ON button_status
        FOR EACH ROW
        BEGIN
            -- Check if the reading timestamp is strictly greater than the sensor's joined timestamp
            SELECT
                CASE
                    WHEN (SELECT joined_at FROM sensor WHERE id = NEW.sensor_id) >= NEW.date
                    THEN RAISE(ABORT, 'Reading timestamp must be strictly after sensor joined timestamp')
            END;
        END;
    """
    )
    pres_check_trigger = DDL(
        """
        CREATE TRIGGER pres_reading_newer_than_join_date
        BEFORE INSERT
        ON pres_status
        FOR EACH ROW
        BEGIN
            -- Check if the reading timestamp is strictly greater than the sensor's joined timestamp
            SELECT
                CASE
                    WHEN (SELECT joined_at FROM sensor WHERE id = NEW.sensor_id) >= NEW.date
                    THEN RAISE(ABORT, 'Reading timestamp must be strictly after sensor joined timestamp')
            END;
        END;
    """
    )
    # sensor_session_check_trigger = DDL(
    #     """
    #     CREATE TRIGGER sensor_session_id_unique_each_time
    #     BEFORE UPDATE
    #     ON sensor
    #     FOR EACH ROW
    #     BEGIN
    #         -- Check if the new session id is different than the old one
    #         SELECT
    #             CASE
    #                 WHEN OLD.session_id = NEW.session_id
    #                 THEN RAISE(ABORT, 'New session ID must be different than the one before')
    #         END;
    #     END;
    # """
    # )
    sensor_joined_at_check_trigger = DDL(
        """
        CREATE TRIGGER sensor_check_join_timestamp_not_in_future
        BEFORE INSERT
        ON sensor
        FOR EACH ROW
        BEGIN
            -- Check if joined timestamp is not in the future
            SELECT
                CASE
                    WHEN NEW.joined_at > datetime('now')
                    THEN RAISE(ABORT, 'Timestamp cannot be in the future')
            END;
        END;
    """
    )
    sensor_last_seen_check_trigger = DDL(
        """
        CREATE TRIGGER sensor_check_last_seen_not_in_future
        BEFORE INSERT
        ON sensor
        FOR EACH ROW
        BEGIN
            -- Check if last seen timestamp is not in the future
            SELECT
                CASE
                    WHEN NEW.last_seen > datetime('now')
                    THEN RAISE(ABORT, 'Timestamp cannot be in the future')
            END;
        END;
    """
    )
    sensor_joined_at_immutable_trigger = DDL(
        """
        CREATE TRIGGER sensor_check_join_timestamp_immutable
        BEFORE UPDATE
        ON sensor
        FOR EACH ROW
        WHEN NEW.joined_at != OLD.joined_at
        BEGIN
            -- Prevent updates to joined_at after insertion
            SELECT RAISE(ABORT, 'joined_at cannot be modified after insertion');
        END;
    """
    )
    led_date_check_trigger = DDL(
        """
        CREATE TRIGGER led_check_date_not_in_future
        BEFORE INSERT
        ON led_status
        FOR EACH ROW
        BEGIN
            -- Check if date timestamp is not in the future
            SELECT
                CASE
                    WHEN NEW.date > datetime('now')
                    THEN RAISE(ABORT, 'Timestamp cannot be in the future')
            END;
        END;
    """
    )
    led_date_immutable_trigger = DDL(
        """
        CREATE TRIGGER led_check_date_immutable
        BEFORE UPDATE
        ON led_status
        FOR EACH ROW
        WHEN NEW.date != OLD.date
        BEGIN
            -- Prevent updates to date after insertion
            SELECT RAISE(ABORT, 'date cannot be modified after insertion');
        END;
    """
    )

    button_date_check_trigger = DDL(
        """
        CREATE TRIGGER button_check_date_not_in_future
        BEFORE INSERT
        ON button_status
        FOR EACH ROW
        BEGIN
            -- Check if date timestamp is not in the future
            SELECT
                CASE
                    WHEN NEW.date > datetime('now')
                    THEN RAISE(ABORT, 'Timestamp cannot be in the future')
            END;
        END;
    """
    )
    button_date_immutable_trigger = DDL(
        """
        CREATE TRIGGER button_check_date_immutable
        BEFORE UPDATE
        ON button_status
        FOR EACH ROW
        WHEN NEW.date != OLD.date
        BEGIN
            -- Prevent updates to date after insertion
            SELECT RAISE(ABORT, 'date cannot be modified after insertion');
        END;
    """
    )
    pres_date_check_trigger = DDL(
        """
        CREATE TRIGGER pres_check_date_not_in_future
        BEFORE INSERT
        ON pres_status
        FOR EACH ROW
        BEGIN
            -- Check if date timestamp is not in the future
            SELECT
                CASE
                    WHEN NEW.date > datetime('now')
                    THEN RAISE(ABORT, 'Timestamp cannot be in the future')
            END;
        END;
    """
    )
    pres_date_immutable_trigger = DDL(
        """
        CREATE TRIGGER pres_check_date_immutable
        BEFORE UPDATE
        ON pres_status
        FOR EACH ROW
        WHEN NEW.date != OLD.date
        BEGIN
            -- Prevent updates to date after insertion
            SELECT RAISE(ABORT, 'date cannot be modified after insertion');
        END;
    """
    )
    event.listen(
        LedStatus.metadata,
        "after_create",
        led_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        ButtonStatus.metadata,
        "after_create",
        button_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        PhotoresistorStatus.metadata,
        "after_create",
        pres_check_trigger.execute_if(dialect="sqlite"),
    )
    # event.listen(
    #     Sensor.metadata,
    #     "after_create",
    #     sensor_session_check_trigger.execute_if(dialect="sqlite"),
    # )
    event.listen(
        Sensor.metadata,
        "after_create",
        sensor_joined_at_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        Sensor.metadata,
        "after_create",
        sensor_joined_at_immutable_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        Sensor.metadata,
        "after_create",
        sensor_last_seen_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        LedStatus.metadata,
        "after_create",
        led_date_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        LedStatus.metadata,
        "after_create",
        led_date_immutable_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        ButtonStatus.metadata,
        "after_create",
        button_date_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        ButtonStatus.metadata,
        "after_create",
        button_date_immutable_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        PhotoresistorStatus.metadata,
        "after_create",
        pres_date_check_trigger.execute_if(dialect="sqlite"),
    )
    event.listen(
        PhotoresistorStatus.metadata,
        "after_create",
        pres_date_immutable_trigger.execute_if(dialect="sqlite"),
    )
    # event.listen(
    #     BasicStatus.metadata, "before_drop", check_trigger.execute_if(dialect="sqlite")
    # )

    engine = create_engine("sqlite:///db.sqlite3", echo=True)
    Base.metadata.create_all(engine)
