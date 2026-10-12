import { defineRailway, github, project, service } from "railway/iac";
// This repository manages only its own resources in the environment. Other
// repositories export their own partial name.
// See https://docs.railway.com/infrastructure-as-code#multi-repo-projects
export const partial = "carbon-credits";
export default defineRailway(() => {
  const carbonCredits = service("carbon-credits", {
    // builder from CaC: "DOCKERFILE"
    source: github("surazbissoyi/carbon-credits", { branch: "claude/blissful-turing-odiwcf", checkSuites: false }),
    healthcheck: "/api/health",
    healthcheckTimeout: 300,
    replicas: { "iad": 1 },
  });

  return project("carbon-credits", {
    variables: { managed: false },
    resources: [carbonCredits],
  });
});
