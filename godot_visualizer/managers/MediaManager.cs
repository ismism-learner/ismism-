using Godot;
using System.Collections.Generic;

namespace Managers
{
    public class Media
    {
        public string Title { get; set; }
        public string AuthorId { get; set; }
        public string IdeologyId { get; set; }
        public float InfluenceStrength { get; set; }

        public Media(string title, string authorId, string ideologyId, float influence)
        {
            Title = title;
            AuthorId = authorId;
            IdeologyId = ideologyId;
            InfluenceStrength = influence;
        }
    }

    public partial class MediaManager : Node
    {
        private static readonly RandomNumberGenerator Rng = new();
        public List<Media> PublishedMedia { get; private set; } = new List<Media>();

        public void Publish(Media newMedia)
        {
            PublishedMedia.Add(newMedia);
            GD.Print($"MEDIA: {newMedia.AuthorId} has published '{newMedia.Title}' spreading ideology {newMedia.IdeologyId}.");
        }

        public Media ConsumeRandomMedia()
        {
            if (PublishedMedia.Count == 0) return null;

            int index = Rng.RandiRange(0, PublishedMedia.Count - 1);
            return PublishedMedia[index];
        }
    }
}