using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using SpaceWar.Core.States;

namespace SpaceWar.Core;

public class Game1 : Game
{
    private readonly GraphicsDeviceManager graphics;
    private SpriteBatch spriteBatch;
    private GameStateMachine stateMachine;

    public Game1()
    {
        graphics = new GraphicsDeviceManager(this);
        Content.RootDirectory = "Content";
        IsMouseVisible = true;
    }

    protected override void Initialize()
    {
        base.Initialize();

        stateMachine = new GameStateMachine(this);
        var menuState = new MenuState(this, stateMachine);
        stateMachine.AddState(menuState);
        stateMachine.TransitionTo<MenuState>();
    }

    protected override void LoadContent()
    {
        spriteBatch = new SpriteBatch(GraphicsDevice);
    }

    protected override void UnloadContent()
    {
        Content.Unload();
        base.UnloadContent();
    }

    protected override void Update(GameTime gameTime)
    {
        stateMachine.Update(gameTime);
        base.Update(gameTime);
    }

    protected override void Draw(GameTime gameTime)
    {
        GraphicsDevice.Clear(Color.Black);
        stateMachine.Draw(gameTime);
        base.Draw(gameTime);
    }
}
