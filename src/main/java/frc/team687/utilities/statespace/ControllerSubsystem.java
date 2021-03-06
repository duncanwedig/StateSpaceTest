package frc.team687.utilities.statespace;

import Jama.Matrix;
import edu.wpi.first.wpilibj.command.Subsystem;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;

abstract public class ControllerSubsystem extends Subsystem {

    protected Matrix m_currentOutput;

    private StateSpaceGains[] m_gains;
    private StateSpaceController m_controller;
    private StateSpaceObserver m_observer;
    private int m_gainsIndex;

    private boolean m_isInverted;

    public ControllerSubsystem(StateSpaceGains gains, Matrix U_min, Matrix U_max, Matrix initialState,
                               Matrix initialInput, int initialIndex) {
        this(new StateSpaceGains[]{gains}, U_min, U_max, initialState, initialInput, initialIndex);
    }

    public ControllerSubsystem(StateSpaceGains[] gains, Matrix U_min, Matrix U_max, Matrix initialState,
                                Matrix initialInput, int initialIndex) {
        this.m_gains = gains;
        this.m_controller = new StateSpaceController(this.m_gains, U_min, U_max);
        this.m_observer = new StateSpaceObserver(this.m_gains, initialState);
        this.m_gainsIndex = initialIndex;
        this.setGainsIndex(m_gainsIndex);

        this.m_currentOutput = initialInput;

    }

    protected void setGainsIndex(int newIndex) {
        this.m_controller.setGainsIndex(0);
        this.m_observer.setGainsIndex(0);
    }

    protected void setInverted(boolean inverted) {
        this.m_isInverted = inverted;
    }

    protected Matrix trackReference(Matrix reference, Matrix measurement) {
        Matrix estimatedState = this.m_observer.newStateEstimate(this.m_currentOutput, measurement);
        this.m_currentOutput = this.m_controller.getBoundedOutput(reference, estimatedState);
        if (m_isInverted) {
            return this.m_currentOutput.times(-1);
        } else {
            return this.m_currentOutput;
        }
    }

    protected void updateWithInput(Matrix input, Matrix measurement) {
        Matrix estimatedState = this.m_observer.newStateEstimate(this.m_currentOutput, measurement);
        this.m_currentOutput = input;
    }

    protected Matrix getXHat() {
        return this.m_observer.getCurrentStateEstimate();
    }

    protected void setXHat(Matrix xHat) {
        this.m_observer.setXHat(xHat);
    }

}
