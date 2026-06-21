import { BookOpen, Code2, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui-core";

interface Skill {
  name: string;
  uri: string;
  content?: string;
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selected, setSelected] = useState<Skill | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const resp = await fetch("/api/skills");
        const data = await resp.json();
        setSkills(data.skills || []);
      } catch {
        // Fall back to sota manifest
        try {
          const resp = await fetch("/api/sota");
          const data = await resp.json();
          if (data.features?.skills_uris) {
            const skillList = data.features.skills_uris.map((uri: string) => ({
              name: uri.replace("skill://", "").replace("/SKILL.md", ""),
              uri,
            }));
            setSkills(skillList);
          }
        } catch {
          setSkills([
            { name: "gimp-expert", uri: "skill://gimp-expert/SKILL.md" },
          ]);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchSkills();
  }, []);

  const loadSkill = async (skill: Skill) => {
    if (skill.content) {
      setSelected(skill);
      return;
    }
    setLoading(true);
    try {
      const resp = await fetch(`/api/skills/${skill.name}`);
      const data = await resp.json();
      const updated = {
        ...skill,
        content: data.content || data.markdown || "# No content available",
      };
      setSkills((s) => s.map((sk) => (sk.name === skill.name ? updated : sk)));
      setSelected(updated);
    } catch {
      setSelected({
        ...skill,
        content: "# Error\nCould not load skill content.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Skills</h2>
        <p className="text-muted-foreground mt-1">
          FastMCP 3.2 skills provider — Markdown resources for AI agents
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : (
            skills.map((skill) => (
              <button
                key={skill.name}
                onClick={() => loadSkill(skill)}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  selected?.name === skill.name
                    ? "bg-primary/10 border-primary/30"
                    : "bg-card/60 border-border/30 hover:border-primary/20"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <BookOpen className="w-4 h-4 text-primary" />
                  <span className="font-mono text-sm font-medium">
                    {skill.name}
                  </span>
                </div>
                <span className="text-[10px] text-muted-foreground font-mono">
                  {skill.uri}
                </span>
              </button>
            ))
          )}
        </div>

        <div className="md:col-span-2">
          {selected?.content ? (
            <Card className="overflow-hidden">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Code2 className="w-5 h-5 text-primary" />
                  {selected.uri}
                </CardTitle>
                <CardDescription>
                  Skill documentation for AI agents
                </CardDescription>
              </CardHeader>
              <CardContent className="prose prose-invert prose-sm max-w-none prose-headings:text-foreground prose-code:text-primary prose-pre:bg-secondary prose-a:text-primary">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {selected.content}
                </ReactMarkdown>
              </CardContent>
            </Card>
          ) : (
            <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              ) : (
                "Select a skill to view its content"
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
