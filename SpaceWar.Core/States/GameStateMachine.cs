using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;

namespace SpaceWar.Core.States
{
    public class GameStateMachine
    {
        private IGameState currentState;
        private readonly Dictionary<Type, IGameState> states;
        private readonly Game game;

        public GameStateMachine(Game game)
        {
            this.game = game;
            states = new Dictionary<Type, IGameState>();
        }

        public void AddState<T>(T state) where T : IGameState
        {
            var type = typeof(T);
            if (!states.ContainsKey(type))
            {
                states[type] = state;
                state.Initialize();
                state.LoadContent();
            }
        }

        public void RemoveState<T>() where T : IGameState
        {
            var type = typeof(T);
            if (states.ContainsKey(type))
            {
                if (currentState != null && currentState.GetType() == type)
                {
                    currentState.OnExit();
                    currentState = null;
                }

                states[type].UnloadContent();
                states.Remove(type);
            }
        }

        public void TransitionTo<T>() where T : IGameState
        {
            var type = typeof(T);
            if (states.TryGetValue(type, out var nextState))
            {
                currentState?.OnExit();
                currentState = nextState;
                currentState.OnEnter();
            }
        }

        public void Update(GameTime gameTime)
        {
            currentState?.Update(gameTime);
        }

        public void Draw(GameTime gameTime)
        {
            currentState?.Draw(gameTime);
        }
    }
} 