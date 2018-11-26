package dk.itu.mario.engine.sonar;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

import javax.sound.sampled.*;


import dk.itu.mario.engine.sonar.mixer.ListenerMixer;

import dk.itu.mario.engine.sonar.sample.SamplePlayer;
import dk.itu.mario.engine.sonar.sample.SonarSample;
import dk.itu.mario.engine.sonar.sample.SampleLoader;



public class SonarSoundEngine implements Runnable
{
    private SonarSample silentSample;
    private SourceDataLine sdl;
    private int rate = 44100;
    private ListenerMixer listenerMixer;
    private int bufferSize = rate / 100; // 10 ms
    private ByteBuffer soundBuffer = ByteBuffer.allocate(bufferSize * 4);
    private float[] leftBuf, rightBuf;
    private float amplitude = 1;
    private float targetAmplitude = 1;
    private boolean alive = true;

    protected SonarSoundEngine()
    {
    }

    public SonarSoundEngine(int maxChannels) throws LineUnavailableException
    {
        silentSample = new SonarSample(new float[] {0}, 44100);
        Mixer mixer = AudioSystem.getMixer(null);

        sdl = (SourceDataLine) mixer.getLine(new Line.Info(SourceDataLine.class));
        sdl.open(new AudioFormat(rate, 16, 2, true, false), bufferSize * 2 * 2 * 2 * 2 * 2);
        soundBuffer.order(ByteOrder.LITTLE_ENDIAN);
        sdl.start();

        try
        {
/*            FloatControl volumeControl = (FloatControl) sdl.getControl(FloatControl.Type.MASTER_GAIN);
            volumeControl.setValue(volumeControl.getMaximum());*/
        }
        catch (IllegalArgumentException e)
        {
            System.out.println("Failed to set the sound volume");
        }

        listenerMixer = new ListenerMixer(maxChannels);

        leftBuf = new float[bufferSize];
        rightBuf = new float[bufferSize];

        Thread thread = new Thread(this);
        thread.setDaemon(true);
        thread.setPriority(10);
        thread.start();
    }

    public void setListener(SoundListener soundListener)
    {
        listenerMixer.setSoundListener(soundListener);
    }

    public void shutDown()
    {
        alive = false;
    }

    public SonarSample loadSample(String resourceName)
    {
        try
        {
            return SampleLoader.loadSample(resourceName);
        }
        catch (Exception e)
        {
            System.out.println("Failed to load sample " + resourceName + ". Using silent sample");
            e.printStackTrace();
            return silentSample;
        }
    }

    public void play(SonarSample sample, SoundSource soundSource, float volume, float priority, float rate)
    {
        synchronized (listenerMixer)
        {
        	if(!dk.itu.mario.engine.Art.mute)
        		listenerMixer.addSoundProducer(new SamplePlayer((SonarSample) sample, rate), soundSource, volume, priority);
        }
    }

    public void clientTick(float alpha)
    {
        synchronized (listenerMixer)
        {
            listenerMixer.update(alpha);
        }
    }

    public void tick()
    {
        soundBuffer.clear();

        //        targetAmplitude = (targetAmplitude - 1) * 0.9f + 1;
        //        targetAmplitude = (targetAmplitude - 1) * 0.9f + 1;
        synchronized (listenerMixer)
        {
            float maxAmplitude = listenerMixer.read(leftBuf, rightBuf, rate);
            //            if (maxAmplitude > targetAmplitude) targetAmplitude = maxAmplitude;
        }

        soundBuffer.clear();
        float gain = 32000;
        for (int i = 0; i < bufferSize; i++)
        {
            //            amplitude += (targetAmplitude - amplitude) / rate;
            //          amplitude = 1;
            //              float gain = 30000;
            int l = (int) (leftBuf[i] * gain);
            int r = (int) (rightBuf[i] * gain);
            if (l > 32767) l = 32767;
            if (r > 32767) r = 32767;
            if (l < -32767) l = -32767;
            if (r < -32767) r = -32767;
            soundBuffer.putShort((short)l);
            soundBuffer.putShort((short)r);
        }

        sdl.write(soundBuffer.array(), 0, bufferSize * 2 * 2);
    }

    public void run()
    {
        while (alive)
        {
            tick();
        }
    }
}
