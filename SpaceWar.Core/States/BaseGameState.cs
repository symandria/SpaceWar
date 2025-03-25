using Microsoft.Xna.Framework;

namespace SpaceWar.Core.States
{
    public abstract class BaseGameState : IGameState
    {
        protected readonly Game Game;
        protected readonly GameStateMachine StateMachine;

        protected BaseGameState(Game game, GameStateMachine stateMachine)
        {
            Game = game;
            StateMachine = stateMachine;
        }

        public virtual void Initialize() { }
        public virtual void LoadContent() { }
        public virtual void UnloadContent() { }
        public virtual void Update(GameTime gameTime) { }
        public virtual void Draw(GameTime gameTime) { }
        public virtual void OnEnter() { }
        public virtual void OnExit() { }
    }
} 