package dk.itu.mario.engine.util;

import java.awt.Graphics;

public abstract class UIItem{

	protected int x,y;
	protected boolean selected;
	protected int width,height;

	public abstract void render(Graphics g);
	public abstract void prev();
	public abstract void next();

	public void setSelected(){
		selected = true;
	}

	public void setUnselected(){
		selected = false;
	}
}
