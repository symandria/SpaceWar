using Microsoft.Xna.Framework;

namespace SpaceWar.Core.States
{
    public interface IGameState
    {
        void Initialize();
        void LoadContent();
        void UnloadContent();
        void Update(GameTime gameTime);
        void Draw(GameTime gameTime);
        void OnEnter();
        void OnExit();
    }
} 