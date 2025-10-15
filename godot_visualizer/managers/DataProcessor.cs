using Godot;
using Godot.Collections;
using System.Linq;

namespace Managers
{
    public partial class DataProcessor : Node
    {
        public void ProcessAndSaveIsms(string rawIsmsPath, string rulesPath, string outputPath)
        {
            var ismsArray = LoadJsonArray(rawIsmsPath);
            if (ismsArray == null) return;

            var rules = LoadJsonDictionary(rulesPath);
            if (rules == null) return;

            var processedIsms = new Dictionary();
            var allIsmsList = new Array<Dictionary>();

            // First pass: Add keywords and convert to a list of dictionaries for easier processing
            foreach (var ismVariant in ismsArray)
            {
                var ism = (Dictionary)ismVariant;
                var newIsm = new Dictionary(ism);

                var keywords = new Array<string>();
                var philosophy = (Dictionary)newIsm["philosophy"];

                // Extract keywords from all philosophy fields
                foreach (var key in philosophy.Keys)
                {
                    var value = philosophy[key];
                    if (value is string strValue)
                    {
                        keywords.Add(strValue);
                    }
                    else if (value is Dictionary dictValue)
                    {
                        if (dictValue.Contains("base")) keywords.Add(dictValue["base"].ToString());
                        if (dictValue.Contains("counter")) keywords.Add(dictValue["counter"].ToString());
                    }
                }
                newIsm["keywords"] = keywords;
                allIsmsList.Add(newIsm);
            }

            // Second pass: Generate parent-child relationships and format the final dictionary
            foreach (var ism in allIsmsList)
            {
                var ismId = ism["id"].ToString();
                var ismKeywords = (Array<string>)ism["keywords"];

                (string parentId, int maxOverlap) = FindBestParent(ismId, ismKeywords, allIsmsList);

                if (parentId != null && maxOverlap > 2) // Require a decent overlap
                {
                    ism["parent_ism"] = parentId;
                    var parentIsm = allIsmsList.First(p => p["id"].ToString() == parentId);
                    var parentKeywords = (Array<string>)parentIsm["keywords"];
                    var triggerKeyword = ismKeywords.Intersect(parentKeywords).First(); // Simple trigger
                    ism["birth_trigger"] = triggerKeyword;
                }

                processedIsms[ismId] = ism;
            }


            SaveJsonFile(processedIsms, outputPath);
            GD.Print($"Processed and saved {processedIsms.Count} isms to {outputPath}");
        }

        private (string, int) FindBestParent(string currentIsmId, Array<string> currentKeywords, Array<Dictionary> allIsms)
        {
            string bestParentId = null;
            int maxOverlap = 0;

            foreach (var potentialParent in allIsms)
            {
                var potentialParentId = potentialParent["id"].ToString();
                if (potentialParentId == currentIsmId) continue;

                var potentialParentKeywords = (Array<string>)potentialParent["keywords"];
                var overlap = currentKeywords.Intersect(potentialParentKeywords).Count();

                if (overlap > maxOverlap)
                {
                    maxOverlap = overlap;
                    bestParentId = potentialParentId;
                }
            }

            return (bestParentId, maxOverlap);
        }

        private Array LoadJsonArray(string path)
        {
            var content = FileAccess.GetFileAsString(path);
            var json = new Json();
            if (json.Parse(content) != Error.Ok)
            {
                GD.PushError($"Failed to parse JSON array from: {path}");
                return null;
            }
            return (Array)json.Data;
        }

        private Dictionary LoadJsonDictionary(string path)
        {
            var content = FileAccess.GetFileAsString(path);
            var json = new Json();
            if (json.Parse(content) != Error.Ok)
            {
                GD.PushError($"Failed to parse JSON dictionary from: {path}");
                return null;
            }
            return (Dictionary)json.Data;
        }

        private void SaveJsonFile(Dictionary data, string path)
        {
            var jsonString = Json.Stringify(data, "  ");
            using var file = FileAccess.Open(path, FileAccess.ModeFlags.Write);
            if (file == null)
            {
                GD.PushError($"Failed to open file for writing: {path}");
                return;
            }
            file.StoreString(jsonString);
        }
    }
}