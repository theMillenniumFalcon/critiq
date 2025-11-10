import { AnalyzeForm } from "@/components/analyze-form";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center h-full py-12 bg-background">
      <div className="w-full max-w-4xl px-4 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">
            AI-Powered Code Review
          </h1>
          <p className="text-xl text-muted-foreground">
            Get instant feedback on your pull requests using advanced AI analysis
          </p>
        </div>
        <AnalyzeForm />
      </div>
    </div>
  );
}