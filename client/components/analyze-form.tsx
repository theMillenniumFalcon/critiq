"use client";

import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, Resolver } from "react-hook-form";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { toast } from "sonner";
import { analyzeAPI, type AnalyzeRequest } from "@/lib/api-client";
import { TaskStatus } from "./task-status";
import { getPrNumberFromUrl, getRepoFromUrl } from "@/lib/utils";

const analyzeFormSchema = z.object({
  repo_url: z.string().url("Please enter a valid GitHub repository URL"),
  pr_number: z.union([
    z.string().refine((val) => val === "", { message: "PR number is required" }),
    z.coerce.number().positive("PR number must be positive")
  ]),
  github_token: z.string().optional(),
});

type AnalyzeFormValues = z.infer<typeof analyzeFormSchema>;

export function AnalyzeForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  const form = useForm<AnalyzeFormValues>({
    resolver: zodResolver(analyzeFormSchema) as Resolver<AnalyzeFormValues>,
    defaultValues: {
      repo_url: "",
      pr_number: 0,
      github_token: "",
    },
  });

  const handleUrlChange = (value: string) => {
    const prNumber = getPrNumberFromUrl(value);
    if (prNumber) {
      form.setValue("pr_number", prNumber);
    }
  };

  async function onSubmit(values: AnalyzeFormValues) {
    try {
      if (typeof values.pr_number === 'string' && values.pr_number === '') {
        toast.error("Please enter a pull request number");
        return;
      }
      
      setIsLoading(true);
      const response = await analyzeAPI.submitAnalysis({
        repo_url: values.repo_url,
        pr_number: values.pr_number as number,
        github_token: values.github_token || undefined,
      } as AnalyzeRequest);

      setActiveTaskId(response.task_id);
      toast.success("Analysis started", {
        description: `Task ID: ${response.task_id}`,
      });
    } catch (error) {
      toast.error("Failed to start analysis", {
        description: error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Analyze Pull Request</CardTitle>
          <CardDescription>
            Submit a GitHub pull request for AI-powered code review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <FormField
                control={form.control}
                name="repo_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Repository URL</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="https://github.com/owner/repo/pull/123"
                        onChange={(e) => {
                          field.onChange(e);
                          handleUrlChange(e.target.value);
                        }}
                        value={field.value}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="pr_number"
                render={({ field: { onChange, value, ...field } }) => (
                  <FormItem>
                    <FormLabel>Pull Request Number</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="123"
                        onChange={(e) => {
                          const val = e.target.value;
                          onChange(val === "" ? val : Number(val));
                        }}
                        value={value ?? ""}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="github_token"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>GitHub Token (Optional)</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="ghp_..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Submitting..." : "Start Analysis"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {activeTaskId && (
        <TaskStatus 
          taskId={activeTaskId} 
          onComplete={() => setActiveTaskId(null)} 
        />
      )}
    </div>
  );
}